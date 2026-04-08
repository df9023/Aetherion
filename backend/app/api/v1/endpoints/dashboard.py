from fastapi import APIRouter, Query
from sqlalchemy import and_, desc, distinct, func, select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession, OrganizationId
from app.models.audit_entry import AuditEntry
from app.models.base import CaseImpactStatus, CaseStatus
from app.models.case import Case
from app.models.case_impact import CaseImpact
from app.models.regulatory_change import RegulatoryChange
from app.schemas.audit_entry import AuditEntryResponse
from app.schemas.regulatory_change import (
    ComplianceHealthResponse,
    RegulatoryChangeResponse,
)

router = APIRouter()


@router.get("/audit/recent", response_model=list[AuditEntryResponse])
async def get_recent_audit(
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
    limit: int = Query(default=10, le=50),
) -> list[AuditEntry]:
    """Get most recent audit entries across all cases for the organization."""
    result = await db.execute(
        select(AuditEntry)
        .join(Case, AuditEntry.case_id == Case.id)
        .where(Case.organization_id == organization_id)
        .order_by(AuditEntry.timestamp.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


@router.get("/dashboard/compliance-health", response_model=ComplianceHealthResponse)
async def get_compliance_health(
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> ComplianceHealthResponse:
    """Firm-wide compliance health snapshot for the dashboard."""
    # Active case count (not archived / not completed)
    result = await db.execute(
        select(func.count(Case.id)).where(
            Case.organization_id == organization_id,
            Case.status.notin_([CaseStatus.ARCHIVED, CaseStatus.COMPLETED]),
        )
    )
    total_active_cases = int(result.scalar_one() or 0)

    # Total open impacts for this org
    result = await db.execute(
        select(func.count(CaseImpact.id)).where(
            CaseImpact.organization_id == organization_id,
            CaseImpact.status == CaseImpactStatus.OPEN,
        )
    )
    total_open_impacts = int(result.scalar_one() or 0)

    # Distinct cases that have at least one open impact
    result = await db.execute(
        select(func.count(distinct(CaseImpact.case_id))).where(
            CaseImpact.organization_id == organization_id,
            CaseImpact.status == CaseImpactStatus.OPEN,
        )
    )
    cases_with_open_impacts = int(result.scalar_one() or 0)

    # Open impacts grouped by regulatory change severity
    result = await db.execute(
        select(RegulatoryChange.severity, func.count(CaseImpact.id))
        .join(
            CaseImpact,
            CaseImpact.regulatory_change_id == RegulatoryChange.id,
        )
        .where(
            CaseImpact.organization_id == organization_id,
            CaseImpact.status == CaseImpactStatus.OPEN,
        )
        .group_by(RegulatoryChange.severity)
    )
    impacts_by_severity: dict[str, int] = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }
    for severity, count in result.all():
        impacts_by_severity[severity.value] = int(count)

    # Recent changes (last 5, newest first)
    result = await db.execute(
        select(RegulatoryChange)
        .options(
            selectinload(RegulatoryChange.creator),
            selectinload(RegulatoryChange.knowledge_item),
            selectinload(RegulatoryChange.case_impacts),
        )
        .where(
            RegulatoryChange.organization_id == organization_id,
            RegulatoryChange.is_active.is_(True),
        )
        .order_by(desc(RegulatoryChange.published_at))
        .limit(5)
    )
    changes = list(result.scalars().all())
    recent_changes: list[RegulatoryChangeResponse] = []
    for c in changes:
        resp = RegulatoryChangeResponse.model_validate(c)
        resp.impact_count = len(c.case_impacts or [])
        resp.open_impact_count = sum(
            1 for i in (c.case_impacts or []) if i.status == CaseImpactStatus.OPEN
        )
        recent_changes.append(resp)

    return ComplianceHealthResponse(
        total_active_cases=total_active_cases,
        cases_with_open_impacts=cases_with_open_impacts,
        total_open_impacts=total_open_impacts,
        impacts_by_severity=impacts_by_severity,
        recent_changes=recent_changes,
    )
