import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession, OrganizationId
from app.config import get_settings
from app.models.case import Case
from app.models.client import Client
from app.models.audit_entry import AuditEntry
from app.models.base import (
    AuditAction,
    ActorType,
    CaseType,
    RecommendationType,
)
from app.models.recommendation import Recommendation
from app.schemas.case import CaseCreate, CaseUpdate, CaseResponse
from app.schemas.audit_entry import AuditEntryResponse
from app.schemas.recommendation import GenerateRecommendationRequest, RecommendationResponse
from app.services.memory import MemoryService
from app.services.reasoner import ReasonerService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_in: CaseCreate,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> Case:
    case = Case(
        **case_in.model_dump(),
        organization_id=organization_id,
    )
    db.add(case)
    await db.flush()

    # Create audit entry
    audit = AuditEntry(
        case_id=case.id,
        action=AuditAction.CASE_CREATED,
        actor_id=current_user.id,
        actor_type=ActorType.USER,
        details={"case_type": case.case_type.value},
    )
    db.add(audit)
    await db.flush()
    await db.refresh(case)
    return case


@router.get("", response_model=list[CaseResponse])
async def list_cases(
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
    skip: int = 0,
    limit: int = 100,
) -> list[Case]:
    result = await db.execute(
        select(Case)
        .where(Case.organization_id == organization_id)
        .order_by(Case.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> Case:
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.organization_id == organization_id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


@router.patch("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: UUID,
    case_in: CaseUpdate,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> Case:
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.organization_id == organization_id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    update_data = case_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)

    await db.flush()
    await db.refresh(case)
    return case


@router.get("/{case_id}/audit", response_model=list[AuditEntryResponse])
async def get_case_audit_trail(
    case_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> list[AuditEntry]:
    # Verify case belongs to organization
    case_result = await db.execute(
        select(Case).where(Case.id == case_id, Case.organization_id == organization_id)
    )
    if not case_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    result = await db.execute(
        select(AuditEntry)
        .where(AuditEntry.case_id == case_id)
        .order_by(AuditEntry.timestamp.desc())
    )
    return list(result.scalars().all())


@router.get("/{case_id}/recommendations", response_model=list[RecommendationResponse])
async def list_case_recommendations(
    case_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> list[Recommendation]:
    # Verify case belongs to org
    case_result = await db.execute(
        select(Case).where(Case.id == case_id, Case.organization_id == organization_id)
    )
    if not case_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.case_id == case_id)
        .order_by(Recommendation.version.desc())
    )
    return list(result.scalars().all())


# CaseType → RecommendationType mapping
_CASE_TYPE_TO_RECOMMENDATION: dict[CaseType, RecommendationType] = {
    CaseType.PENSION_REVIEW: RecommendationType.PRODUCT_SELECTION,
    CaseType.TRANSFER_ADVICE: RecommendationType.TRANSFER,
    CaseType.SALARY_EXCHANGE: RecommendationType.SALARY_EXCHANGE,
    CaseType.RETIREMENT_PLANNING: RecommendationType.WITHDRAWAL_PLAN,
    CaseType.SURVIVOR_PROTECTION: RecommendationType.COVERAGE_CHANGE,
    CaseType.DECUMULATION: RecommendationType.WITHDRAWAL_PLAN,
    CaseType.OTHER: RecommendationType.OTHER,
}


@router.post(
    "/{case_id}/generate-recommendation",
    response_model=RecommendationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_recommendation(
    case_id: UUID,
    body: GenerateRecommendationRequest,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> RecommendationResponse:
    """Generate an AI recommendation for a case.

    This is the core product loop — an advisor clicks "Generate Recommendation"
    in the Workbench and this endpoint fires.
    """
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ANTHROPIC_API_KEY not configured. Cannot generate recommendations.",
        )

    # Load case (org-scoped)
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.organization_id == organization_id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    # Load client
    result = await db.execute(
        select(Client).where(
            Client.id == case.client_id, Client.organization_id == organization_id
        )
    )
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Case has no valid client. Attach a client before generating.",
        )

    # Determine recommendation type
    rec_type = body.recommendation_type or _CASE_TYPE_TO_RECOMMENDATION.get(
        case.case_type, RecommendationType.OTHER
    )

    # Build context dict for the Reasoner prompt
    context = {
        "client": {
            "name": client.name,
            "date_of_birth": str(client.date_of_birth),
            "employment_status": client.employment_status.value,
            "employer_name": client.employer_name,
            "collective_agreement": client.collective_agreement.value,
            "annual_income": str(client.annual_income) if client.annual_income else None,
            "desired_retirement_age": client.desired_retirement_age,
            "risk_profile": client.risk_profile.value if client.risk_profile else None,
        },
        "case": {
            "id": str(case.id),
            "title": case.title,
            "case_type": case.case_type.value,
            "summary": case.summary,
        },
    }
    if body.additional_context:
        context["additional_context"] = body.additional_context

    # Retrieve relevant knowledge via RAG
    memory_service = MemoryService(db)
    search_text = f"{case.title} {case.summary or ''} {case.case_type.value} {client.collective_agreement.value}"
    if body.additional_context:
        search_text += f" {body.additional_context}"

    knowledge_items = await memory_service.get_relevant_knowledge(
        organization_id=organization_id,
        context=search_text,
        limit=5,
    )

    knowledge_dicts = [
        {
            "id": str(item.id),
            "title": item.title,
            "content": item.content,
            "category": item.category.value,
            "source": item.source,
            "tags": item.tags,
        }
        for item in knowledge_items
    ]

    # Generate recommendation via Reasoner
    reasoner = ReasonerService(db)
    recommendation = await reasoner.generate_recommendation(
        case_id=case.id,
        recommendation_type=rec_type,
        context=context,
        knowledge_items=knowledge_dicts,
        created_by=current_user.id,
    )

    await db.commit()
    return recommendation


@router.post("/{case_id}/generate-brief")
async def generate_meeting_brief(
    case_id: UUID,
    body: GenerateRecommendationRequest,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> dict:
    """Generate an AI meeting preparation brief for a case.

    An advisor clicks 'Prepare Meeting' in the Workbench and this endpoint fires.
    Returns the raw structured brief (not persisted to DB).
    """
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ANTHROPIC_API_KEY not configured. Cannot generate meeting brief.",
        )

    # Load case (org-scoped)
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.organization_id == organization_id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    # Load client
    result = await db.execute(
        select(Client).where(
            Client.id == case.client_id, Client.organization_id == organization_id
        )
    )
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Case has no valid client. Attach a client before generating.",
        )

    # Build context dict
    context = {
        "client": {
            "name": client.name,
            "date_of_birth": str(client.date_of_birth),
            "employment_status": client.employment_status.value,
            "employer_name": client.employer_name,
            "collective_agreement": client.collective_agreement.value,
            "annual_income": str(client.annual_income) if client.annual_income else None,
            "desired_retirement_age": client.desired_retirement_age,
            "risk_profile": client.risk_profile.value if client.risk_profile else None,
        },
        "case": {
            "id": str(case.id),
            "title": case.title,
            "case_type": case.case_type.value,
            "summary": case.summary,
        },
    }

    # Retrieve relevant knowledge via RAG
    memory_service = MemoryService(db)
    search_text = f"{case.title} {case.summary or ''} {case.case_type.value} {client.collective_agreement.value} mötesförberedelse"
    if body.additional_context:
        search_text += f" {body.additional_context}"

    knowledge_items = await memory_service.get_relevant_knowledge(
        organization_id=organization_id,
        context=search_text,
        limit=5,
    )

    knowledge_dicts = [
        {
            "id": str(item.id),
            "title": item.title,
            "content": item.content,
            "category": item.category.value,
            "source": item.source,
            "tags": item.tags,
        }
        for item in knowledge_items
    ]

    # Generate meeting brief via Reasoner
    reasoner = ReasonerService(db)
    brief = await reasoner.generate_meeting_brief(
        case_id=case.id,
        context=context,
        knowledge_items=knowledge_dicts,
        additional_context=body.additional_context,
    )

    # Audit entry
    audit = AuditEntry(
        case_id=case.id,
        action=AuditAction.MEETING_BRIEF_GENERATED,
        actor_id=current_user.id,
        actor_type=ActorType.SYSTEM,
        details={
            "llm_model": "claude-sonnet-4-20250514",
            "prompt_template": "meeting_brief.j2",
            "knowledge_items_retrieved": [str(item.id) for item in knowledge_items],
        },
    )
    db.add(audit)
    await db.commit()

    return brief
