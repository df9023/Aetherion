from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession, OrganizationId
from app.models.case import Case
from app.models.audit_entry import AuditEntry
from app.models.base import AuditAction, ActorType
from app.schemas.case import CaseCreate, CaseUpdate, CaseResponse
from app.schemas.audit_entry import AuditEntryResponse

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
