import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import case as sa_case, desc, or_, select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession, OrganizationId
from app.models.audit_entry import AuditEntry
from app.models.base import ActorType, AuditAction, FirmInsightCategory, UserRole
from app.models.case import Case
from app.models.client import Client
from app.models.firm_insight import FirmInsight
from app.schemas.firm_insight import (
    FirmInsightCreate,
    FirmInsightResponse,
    FirmInsightUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _select_with_relations():
    return select(FirmInsight).options(
        selectinload(FirmInsight.creator),
        selectinload(FirmInsight.client_organization),
        selectinload(FirmInsight.source_case),
    )


@router.post("", response_model=FirmInsightResponse, status_code=status.HTTP_201_CREATED)
async def create_firm_insight(
    payload: FirmInsightCreate,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> FirmInsight:
    # Validate source_case_id belongs to the same organization
    if payload.source_case_id is not None:
        result = await db.execute(
            select(Case).where(
                Case.id == payload.source_case_id,
                Case.organization_id == organization_id,
            )
        )
        if result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="source_case_id does not belong to this organization",
            )

    insight = FirmInsight(
        organization_id=organization_id,
        created_by=current_user.id,
        title=payload.title,
        content=payload.content,
        category=payload.category,
        case_types=payload.case_types or [],
        collective_agreements=payload.collective_agreements or [],
        client_organization_id=payload.client_organization_id,
        tags=payload.tags or [],
        source_case_id=payload.source_case_id,
        is_active=True,
        upvotes=0,
        upvoted_by=[],
    )
    db.add(insight)
    await db.flush()

    # Audit entry
    audit = AuditEntry(
        case_id=payload.source_case_id,
        action=AuditAction.INSIGHT_CREATED,
        actor_id=current_user.id,
        actor_type=ActorType.USER,
        details={
            "insight_id": str(insight.id),
            "title": insight.title,
            "category": insight.category.value,
        },
    )
    db.add(audit)
    await db.flush()

    # Re-fetch with relationships loaded
    result = await db.execute(
        _select_with_relations().where(FirmInsight.id == insight.id)
    )
    return result.scalar_one()


@router.get("", response_model=list[FirmInsightResponse])
async def list_firm_insights(
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
    case_type: Optional[str] = Query(None),
    collective_agreement: Optional[str] = Query(None),
    client_organization_id: Optional[UUID] = Query(None),
    category: Optional[FirmInsightCategory] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
) -> list[FirmInsight]:
    stmt = _select_with_relations().where(
        FirmInsight.organization_id == organization_id,
        FirmInsight.is_active.is_(True),
    )

    if case_type:
        stmt = stmt.where(FirmInsight.case_types.any(case_type))
    if collective_agreement:
        stmt = stmt.where(
            FirmInsight.collective_agreements.any(collective_agreement)
        )
    if client_organization_id is not None:
        stmt = stmt.where(FirmInsight.client_organization_id == client_organization_id)
    if category is not None:
        stmt = stmt.where(FirmInsight.category == category)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                FirmInsight.title.ilike(pattern),
                FirmInsight.content.ilike(pattern),
            )
        )

    stmt = stmt.order_by(
        desc(FirmInsight.upvotes), desc(FirmInsight.created_at)
    ).offset(skip).limit(limit)

    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/relevant", response_model=list[FirmInsightResponse])
async def list_relevant_firm_insights(
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
    case_id: UUID = Query(..., description="Case to find relevant insights for"),
) -> list[FirmInsight]:
    # Load case + client (for collective_agreement + client_organization_id)
    result = await db.execute(
        select(Case)
        .options(selectinload(Case.client))
        .where(
            Case.id == case_id,
            Case.organization_id == organization_id,
        )
    )
    case_obj = result.scalar_one_or_none()
    if case_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )

    client: Optional[Client] = case_obj.client
    case_type_value = case_obj.case_type.value
    agreement_value = (
        client.collective_agreement.value if client and client.collective_agreement else None
    )
    client_org_id = client.client_organization_id if client else None

    # Match conditions: any scoping that fits
    case_type_match = FirmInsight.case_types.any(case_type_value)
    agreement_match = (
        FirmInsight.collective_agreements.any(agreement_value)
        if agreement_value is not None
        else None
    )
    client_org_match = (
        FirmInsight.client_organization_id == client_org_id
        if client_org_id is not None
        else None
    )

    match_clauses = [case_type_match]
    if agreement_match is not None:
        match_clauses.append(agreement_match)
    if client_org_match is not None:
        match_clauses.append(client_org_match)

    # Specificity score = number of matching scoping fields (int expression)
    specificity = sa_case((case_type_match, 1), else_=0)
    if agreement_match is not None:
        specificity = specificity + sa_case((agreement_match, 1), else_=0)
    if client_org_match is not None:
        specificity = specificity + sa_case((client_org_match, 1), else_=0)

    stmt = (
        _select_with_relations()
        .where(
            FirmInsight.organization_id == organization_id,
            FirmInsight.is_active.is_(True),
            or_(*match_clauses),
        )
        .order_by(
            desc(specificity),
            desc(FirmInsight.upvotes),
            desc(FirmInsight.created_at),
        )
        .limit(10)
    )

    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{insight_id}", response_model=FirmInsightResponse)
async def get_firm_insight(
    insight_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> FirmInsight:
    result = await db.execute(
        _select_with_relations().where(
            FirmInsight.id == insight_id,
            FirmInsight.organization_id == organization_id,
        )
    )
    insight = result.scalar_one_or_none()
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Insight not found"
        )
    return insight


@router.patch("/{insight_id}", response_model=FirmInsightResponse)
async def update_firm_insight(
    insight_id: UUID,
    payload: FirmInsightUpdate,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> FirmInsight:
    result = await db.execute(
        select(FirmInsight).where(
            FirmInsight.id == insight_id,
            FirmInsight.organization_id == organization_id,
        )
    )
    insight = result.scalar_one_or_none()
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Insight not found"
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(insight, field, value)
    await db.flush()

    result = await db.execute(
        _select_with_relations().where(FirmInsight.id == insight.id)
    )
    return result.scalar_one()


@router.delete("/{insight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_firm_insight(
    insight_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> None:
    result = await db.execute(
        select(FirmInsight).where(
            FirmInsight.id == insight_id,
            FirmInsight.organization_id == organization_id,
        )
    )
    insight = result.scalar_one_or_none()
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Insight not found"
        )

    # Only creator or admin may delete
    if insight.created_by != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator or an admin may delete this insight",
        )

    await db.delete(insight)
    await db.flush()
    return None


@router.post("/{insight_id}/upvote", response_model=FirmInsightResponse)
async def upvote_firm_insight(
    insight_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> FirmInsight:
    result = await db.execute(
        select(FirmInsight).where(
            FirmInsight.id == insight_id,
            FirmInsight.organization_id == organization_id,
        )
    )
    insight = result.scalar_one_or_none()
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Insight not found"
        )

    user_id_str = str(current_user.id)
    upvoted_by = list(insight.upvoted_by or [])
    if user_id_str in upvoted_by:
        # Idempotent — already upvoted, return current state
        result = await db.execute(
            _select_with_relations().where(FirmInsight.id == insight.id)
        )
        return result.scalar_one()

    upvoted_by.append(user_id_str)
    insight.upvoted_by = upvoted_by
    insight.upvotes = (insight.upvotes or 0) + 1
    await db.flush()

    result = await db.execute(
        _select_with_relations().where(FirmInsight.id == insight.id)
    )
    return result.scalar_one()
