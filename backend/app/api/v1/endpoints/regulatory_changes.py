import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession, OrganizationId
from app.models.audit_entry import AuditEntry
from app.models.base import (
    ActorType,
    AuditAction,
    CaseImpactStatus,
    CaseStatus,
    RegulatoryChangeSeverity,
    UserRole,
)
from app.models.case import Case
from app.models.case_impact import CaseImpact
from app.models.regulatory_change import RegulatoryChange
from app.schemas.regulatory_change import (
    CaseImpactResolve,
    CaseImpactResponse,
    RegulatoryChangeCreate,
    RegulatoryChangeResponse,
    RegulatoryChangeUpdate,
    ScanResult,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _select_change_with_relations():
    return select(RegulatoryChange).options(
        selectinload(RegulatoryChange.creator),
        selectinload(RegulatoryChange.knowledge_item),
        selectinload(RegulatoryChange.case_impacts),
    )


def _select_impact_with_relations():
    return select(CaseImpact).options(
        selectinload(CaseImpact.case),
        selectinload(CaseImpact.resolver),
        selectinload(CaseImpact.regulatory_change),
    )


async def _load_change_response(
    db, change_id: UUID, organization_id: UUID
) -> RegulatoryChangeResponse:
    result = await db.execute(
        _select_change_with_relations().where(
            RegulatoryChange.id == change_id,
            RegulatoryChange.organization_id == organization_id,
        )
    )
    change = result.scalar_one()
    return _change_to_response(change)


def _change_to_response(change: RegulatoryChange) -> RegulatoryChangeResponse:
    impacts = change.case_impacts or []
    open_count = sum(
        1 for i in impacts if i.status == CaseImpactStatus.OPEN
    )
    resp = RegulatoryChangeResponse.model_validate(change)
    resp.impact_count = len(impacts)
    resp.open_impact_count = open_count
    return resp


@router.post(
    "",
    response_model=RegulatoryChangeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_regulatory_change(
    payload: RegulatoryChangeCreate,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> RegulatoryChangeResponse:
    change = RegulatoryChange(
        organization_id=organization_id,
        created_by=current_user.id,
        title=payload.title,
        description=payload.description,
        source=payload.source,
        source_url=payload.source_url,
        severity=payload.severity,
        affected_case_types=payload.affected_case_types or [],
        affected_agreements=payload.affected_agreements or [],
        affected_tags=payload.affected_tags or [],
        knowledge_item_id=payload.knowledge_item_id,
        published_at=payload.published_at or datetime.now(timezone.utc),
        is_active=True,
    )
    db.add(change)
    await db.flush()

    audit = AuditEntry(
        case_id=None,
        action=AuditAction.REGULATORY_CHANGE_CREATED,
        actor_id=current_user.id,
        actor_type=ActorType.USER,
        details={
            "regulatory_change_id": str(change.id),
            "title": change.title,
            "severity": change.severity.value,
            "source": change.source,
        },
    )
    db.add(audit)
    await db.flush()

    return await _load_change_response(db, change.id, organization_id)


@router.get("", response_model=list[RegulatoryChangeResponse])
async def list_regulatory_changes(
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
    severity: Optional[RegulatoryChangeSeverity] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
) -> list[RegulatoryChangeResponse]:
    stmt = _select_change_with_relations().where(
        RegulatoryChange.organization_id == organization_id,
    )
    if severity is not None:
        stmt = stmt.where(RegulatoryChange.severity == severity)
    if is_active is not None:
        stmt = stmt.where(RegulatoryChange.is_active.is_(is_active))
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                RegulatoryChange.title.ilike(pattern),
                RegulatoryChange.description.ilike(pattern),
                RegulatoryChange.source.ilike(pattern),
            )
        )

    stmt = (
        stmt.order_by(desc(RegulatoryChange.published_at))
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(stmt)
    changes = list(result.scalars().all())
    return [_change_to_response(c) for c in changes]


@router.get("/{change_id}", response_model=RegulatoryChangeResponse)
async def get_regulatory_change(
    change_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> RegulatoryChangeResponse:
    result = await db.execute(
        _select_change_with_relations().where(
            RegulatoryChange.id == change_id,
            RegulatoryChange.organization_id == organization_id,
        )
    )
    change = result.scalar_one_or_none()
    if not change:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regulatory change not found",
        )
    return _change_to_response(change)


@router.patch("/{change_id}", response_model=RegulatoryChangeResponse)
async def update_regulatory_change(
    change_id: UUID,
    payload: RegulatoryChangeUpdate,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> RegulatoryChangeResponse:
    result = await db.execute(
        select(RegulatoryChange).where(
            RegulatoryChange.id == change_id,
            RegulatoryChange.organization_id == organization_id,
        )
    )
    change = result.scalar_one_or_none()
    if not change:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regulatory change not found",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(change, field, value)
    await db.flush()

    return await _load_change_response(db, change.id, organization_id)


@router.delete("/{change_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_regulatory_change(
    change_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> None:
    result = await db.execute(
        select(RegulatoryChange).where(
            RegulatoryChange.id == change_id,
            RegulatoryChange.organization_id == organization_id,
        )
    )
    change = result.scalar_one_or_none()
    if not change:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regulatory change not found",
        )

    if current_user.role != UserRole.ADMIN and change.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator or an admin may delete this regulatory change",
        )

    await db.delete(change)
    await db.flush()
    return None


def _build_match_reason(
    change: RegulatoryChange,
    case: Case,
    matched_case_type: bool,
    matched_agreement: bool,
) -> tuple[str, list[str]]:
    """Return (match_reason, affected_sections)."""
    reasons = []
    affected_sections: list[str] = []
    if matched_case_type:
        reasons.append(
            f"Ärendetyp ({case.case_type.value}) ingår i den reglering som ändrats"
        )
        affected_sections.append("case_type")
    if matched_agreement:
        agreement_value = (
            case.client.collective_agreement.value
            if case.client and case.client.collective_agreement
            else "okänt"
        )
        reasons.append(
            f"Kollektivavtal ({agreement_value}) påverkas av ändringen"
        )
        affected_sections.append("collective_agreement")

    if not reasons:
        reasons.append("Ärendet matchar reglerna i den ändrade bestämmelsen")

    match_reason = f"{change.title}. " + " · ".join(reasons) + "."
    return match_reason, affected_sections


@router.post("/{change_id}/scan", response_model=ScanResult)
async def scan_regulatory_change(
    change_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> ScanResult:
    """Scan active cases and create CaseImpact entries for those that match."""
    result = await db.execute(
        select(RegulatoryChange).where(
            RegulatoryChange.id == change_id,
            RegulatoryChange.organization_id == organization_id,
        )
    )
    change = result.scalar_one_or_none()
    if not change:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regulatory change not found",
        )

    # Load active cases (not archived / not completed) with client for agreement lookup
    result = await db.execute(
        select(Case)
        .options(selectinload(Case.client))
        .where(
            Case.organization_id == organization_id,
            Case.status.notin_(
                [CaseStatus.ARCHIVED, CaseStatus.COMPLETED]
            ),
        )
    )
    cases = list(result.scalars().all())

    # Load existing impacts for this change to skip duplicates
    result = await db.execute(
        select(CaseImpact.case_id).where(
            CaseImpact.regulatory_change_id == change.id,
        )
    )
    existing_case_ids = {row[0] for row in result.all()}

    affected_case_types = set(change.affected_case_types or [])
    affected_agreements = set(change.affected_agreements or [])

    new_impacts: list[CaseImpact] = []
    skipped_existing = 0
    total_matched = 0

    for case in cases:
        case_type_value = case.case_type.value
        agreement_value = (
            case.client.collective_agreement.value
            if case.client and case.client.collective_agreement
            else None
        )

        matched_case_type = (
            bool(affected_case_types) and case_type_value in affected_case_types
        )
        matched_agreement = (
            bool(affected_agreements)
            and agreement_value is not None
            and agreement_value in affected_agreements
        )

        if not (matched_case_type or matched_agreement):
            continue

        total_matched += 1

        if case.id in existing_case_ids:
            skipped_existing += 1
            continue

        match_reason, affected_sections = _build_match_reason(
            change, case, matched_case_type, matched_agreement
        )

        impact = CaseImpact(
            organization_id=organization_id,
            regulatory_change_id=change.id,
            case_id=case.id,
            match_reason=match_reason,
            affected_sections=affected_sections,
            status=CaseImpactStatus.OPEN,
        )
        db.add(impact)
        new_impacts.append(impact)

    await db.flush()

    # Audit entry
    audit = AuditEntry(
        case_id=None,
        action=AuditAction.IMPACT_SCAN_COMPLETED,
        actor_id=current_user.id,
        actor_type=ActorType.USER,
        details={
            "regulatory_change_id": str(change.id),
            "new_impacts": len(new_impacts),
            "skipped_existing": skipped_existing,
            "total_matched_cases": total_matched,
        },
    )
    db.add(audit)
    await db.flush()

    # Re-fetch new impacts with relations for the response
    if new_impacts:
        impact_ids = [i.id for i in new_impacts]
        result = await db.execute(
            _select_impact_with_relations().where(CaseImpact.id.in_(impact_ids))
        )
        loaded_impacts = list(result.scalars().all())
    else:
        loaded_impacts = []

    return ScanResult(
        regulatory_change_id=change.id,
        new_impacts=len(new_impacts),
        skipped_existing=skipped_existing,
        total_matched_cases=total_matched,
        impacts=[CaseImpactResponse.model_validate(i) for i in loaded_impacts],
    )


@router.patch(
    "/case-impacts/{impact_id}/resolve", response_model=CaseImpactResponse
)
async def resolve_case_impact(
    impact_id: UUID,
    payload: CaseImpactResolve,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> CaseImpactResponse:
    result = await db.execute(
        select(CaseImpact).where(
            CaseImpact.id == impact_id,
            CaseImpact.organization_id == organization_id,
        )
    )
    impact = result.scalar_one_or_none()
    if not impact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case impact not found",
        )

    impact.status = CaseImpactStatus.RESOLVED
    impact.resolved_by = current_user.id
    impact.resolved_at = datetime.now(timezone.utc)
    impact.resolution_note = payload.resolution_note
    await db.flush()

    audit = AuditEntry(
        case_id=impact.case_id,
        action=AuditAction.IMPACT_RESOLVED,
        actor_id=current_user.id,
        actor_type=ActorType.USER,
        details={
            "impact_id": str(impact.id),
            "regulatory_change_id": str(impact.regulatory_change_id),
            "resolution_note": payload.resolution_note,
        },
    )
    db.add(audit)
    await db.flush()

    result = await db.execute(
        _select_impact_with_relations().where(CaseImpact.id == impact.id)
    )
    return CaseImpactResponse.model_validate(result.scalar_one())


@router.patch(
    "/case-impacts/{impact_id}/acknowledge",
    response_model=CaseImpactResponse,
)
async def acknowledge_case_impact(
    impact_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> CaseImpactResponse:
    result = await db.execute(
        select(CaseImpact).where(
            CaseImpact.id == impact_id,
            CaseImpact.organization_id == organization_id,
        )
    )
    impact = result.scalar_one_or_none()
    if not impact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case impact not found",
        )

    impact.status = CaseImpactStatus.ACKNOWLEDGED
    await db.flush()

    audit = AuditEntry(
        case_id=impact.case_id,
        action=AuditAction.IMPACT_ACKNOWLEDGED,
        actor_id=current_user.id,
        actor_type=ActorType.USER,
        details={
            "impact_id": str(impact.id),
            "regulatory_change_id": str(impact.regulatory_change_id),
        },
    )
    db.add(audit)
    await db.flush()

    result = await db.execute(
        _select_impact_with_relations().where(CaseImpact.id == impact.id)
    )
    return CaseImpactResponse.model_validate(result.scalar_one())


@router.patch(
    "/case-impacts/{impact_id}/not-applicable",
    response_model=CaseImpactResponse,
)
async def mark_impact_not_applicable(
    impact_id: UUID,
    payload: CaseImpactResolve,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> CaseImpactResponse:
    result = await db.execute(
        select(CaseImpact).where(
            CaseImpact.id == impact_id,
            CaseImpact.organization_id == organization_id,
        )
    )
    impact = result.scalar_one_or_none()
    if not impact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case impact not found",
        )

    impact.status = CaseImpactStatus.NOT_APPLICABLE
    impact.resolved_by = current_user.id
    impact.resolved_at = datetime.now(timezone.utc)
    impact.resolution_note = payload.resolution_note
    await db.flush()

    audit = AuditEntry(
        case_id=impact.case_id,
        action=AuditAction.IMPACT_RESOLVED,
        actor_id=current_user.id,
        actor_type=ActorType.USER,
        details={
            "impact_id": str(impact.id),
            "regulatory_change_id": str(impact.regulatory_change_id),
            "resolution": "not_applicable",
            "resolution_note": payload.resolution_note,
        },
    )
    db.add(audit)
    await db.flush()

    result = await db.execute(
        _select_impact_with_relations().where(CaseImpact.id == impact.id)
    )
    return CaseImpactResponse.model_validate(result.scalar_one())
