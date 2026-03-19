from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, func

from app.api.deps import CurrentUser, DbSession, OrganizationId
from app.models.case import Case
from app.models.evidence import Evidence
from app.models.recommendation import Recommendation
from app.models.audit_entry import AuditEntry
from app.models.base import AuditAction, ActorType, RecommendationStatus, UserRole
from app.schemas.evidence import EvidenceResponse
from app.schemas.recommendation import (
    RecommendationCreate,
    RecommendationUpdate,
    RecommendationResponse,
)

router = APIRouter()


@router.get("/{recommendation_id}/evidence", response_model=list[EvidenceResponse])
async def list_recommendation_evidence(
    recommendation_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> list[Evidence]:
    # Verify recommendation belongs to org via case
    result = await db.execute(
        select(Recommendation)
        .join(Case, Case.id == Recommendation.case_id)
        .where(
            Recommendation.id == recommendation_id,
            Case.organization_id == organization_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found"
        )

    evidence_result = await db.execute(
        select(Evidence)
        .where(Evidence.recommendation_id == recommendation_id)
        .order_by(Evidence.created_at)
    )
    return list(evidence_result.scalars().all())


@router.post("", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
async def create_recommendation(
    rec_in: RecommendationCreate,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> Recommendation:
    # Verify case belongs to organization
    case_result = await db.execute(
        select(Case).where(
            Case.id == rec_in.case_id, Case.organization_id == organization_id
        )
    )
    if not case_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    # Get next version number
    version_result = await db.execute(
        select(func.coalesce(func.max(Recommendation.version), 0) + 1).where(
            Recommendation.case_id == rec_in.case_id
        )
    )
    next_version = version_result.scalar()

    recommendation = Recommendation(
        case_id=rec_in.case_id,
        version=next_version,
        recommendation_type=rec_in.recommendation_type,
        summary=rec_in.summary,
        reasoning_chain=[step.model_dump() for step in rec_in.reasoning_chain],
        assumptions=[a.model_dump() for a in rec_in.assumptions],
        scenarios=[s.model_dump() for s in rec_in.scenarios] if rec_in.scenarios else None,
        suitability_score=rec_in.suitability_score,
        created_by=current_user.id,
    )
    db.add(recommendation)
    await db.flush()

    # Create audit entry
    audit = AuditEntry(
        case_id=rec_in.case_id,
        action=AuditAction.RECOMMENDATION_GENERATED,
        actor_id=current_user.id,
        actor_type=ActorType.USER,
        details={
            "recommendation_id": str(recommendation.id),
            "version": next_version,
            "type": rec_in.recommendation_type.value,
        },
    )
    db.add(audit)
    await db.flush()
    await db.refresh(recommendation)
    return recommendation


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
async def get_recommendation(
    recommendation_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> Recommendation:
    result = await db.execute(
        select(Recommendation)
        .join(Case, Case.id == Recommendation.case_id)
        .where(
            Recommendation.id == recommendation_id,
            Case.organization_id == organization_id,
        )
    )
    recommendation = result.scalar_one_or_none()
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found"
        )
    return recommendation


@router.patch("/{recommendation_id}", response_model=RecommendationResponse)
async def update_recommendation(
    recommendation_id: UUID,
    rec_in: RecommendationUpdate,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> Recommendation:
    result = await db.execute(
        select(Recommendation)
        .join(Case, Case.id == Recommendation.case_id)
        .where(
            Recommendation.id == recommendation_id,
            Case.organization_id == organization_id,
        )
    )
    recommendation = result.scalar_one_or_none()
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found"
        )

    update_data = rec_in.model_dump(exclude_unset=True)

    if "reasoning_chain" in update_data:
        update_data["reasoning_chain"] = [
            step.model_dump() if hasattr(step, "model_dump") else step
            for step in (rec_in.reasoning_chain or [])
        ]
    if "assumptions" in update_data:
        update_data["assumptions"] = [
            a.model_dump() if hasattr(a, "model_dump") else a
            for a in (rec_in.assumptions or [])
        ]
    if "scenarios" in update_data:
        update_data["scenarios"] = (
            [
                s.model_dump() if hasattr(s, "model_dump") else s
                for s in rec_in.scenarios
            ]
            if rec_in.scenarios is not None
            else None
        )

    for field, value in update_data.items():
        setattr(recommendation, field, value)

    # Audit edit
    audit = AuditEntry(
        case_id=recommendation.case_id,
        action=AuditAction.RECOMMENDATION_EDITED,
        actor_id=current_user.id,
        actor_type=ActorType.USER,
        details={"recommendation_id": str(recommendation_id), "fields_updated": list(update_data.keys())},
    )
    db.add(audit)

    await db.flush()
    await db.refresh(recommendation)
    return recommendation


@router.post("/{recommendation_id}/approve", response_model=RecommendationResponse)
async def approve_recommendation(
    recommendation_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> Recommendation:
    result = await db.execute(
        select(Recommendation)
        .join(Case, Case.id == Recommendation.case_id)
        .where(
            Recommendation.id == recommendation_id,
            Case.organization_id == organization_id,
        )
    )
    recommendation = result.scalar_one_or_none()
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found"
        )

    if current_user.role not in (UserRole.COMPLIANCE_REVIEWER, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only compliance reviewers or admins can approve recommendations",
        )

    if recommendation.created_by == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot approve your own recommendation",
        )

    if recommendation.status != RecommendationStatus.PENDING_REVIEW:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Recommendation must be in pending_review status to approve, currently: {recommendation.status.value}",
        )

    recommendation.status = RecommendationStatus.APPROVED
    recommendation.approved_by = current_user.id

    audit = AuditEntry(
        case_id=recommendation.case_id,
        action=AuditAction.RECOMMENDATION_APPROVED,
        actor_id=current_user.id,
        actor_type=ActorType.USER,
        details={"recommendation_id": str(recommendation_id)},
    )
    db.add(audit)

    await db.flush()
    await db.refresh(recommendation)
    return recommendation
