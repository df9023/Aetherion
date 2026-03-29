from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession, OrganizationId
from app.models.audit_entry import AuditEntry
from app.models.case import Case
from app.schemas.audit_entry import AuditEntryResponse

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
