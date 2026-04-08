import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import CaseImpactStatus, ValueEnum

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.case import Case
    from app.models.regulatory_change import RegulatoryChange


class CaseImpact(Base):
    __tablename__ = "case_impacts"
    __table_args__ = (
        UniqueConstraint(
            "regulatory_change_id", "case_id", name="uq_case_impact_change_case"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    regulatory_change_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("regulatory_changes.id"), nullable=False
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False
    )

    match_reason: Mapped[str] = mapped_column(Text, nullable=False)
    affected_sections: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )

    status: Mapped[CaseImpactStatus] = mapped_column(
        ValueEnum(CaseImpactStatus), nullable=False, default=CaseImpactStatus.OPEN
    )
    resolved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolution_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    regulatory_change: Mapped["RegulatoryChange"] = relationship(
        "RegulatoryChange", back_populates="case_impacts"
    )
    case: Mapped["Case"] = relationship("Case", foreign_keys=[case_id])
    resolver: Mapped[Optional["User"]] = relationship("User", foreign_keys=[resolved_by])

    @property
    def case_title(self) -> Optional[str]:
        try:
            return self.case.title if self.case else None
        except Exception:
            return None

    @property
    def case_status(self) -> Optional[str]:
        try:
            return self.case.status.value if self.case and self.case.status else None
        except Exception:
            return None

    @property
    def resolver_name(self) -> Optional[str]:
        try:
            return self.resolver.name if self.resolver else None
        except Exception:
            return None

    @property
    def regulatory_change_title(self) -> Optional[str]:
        try:
            return (
                self.regulatory_change.title if self.regulatory_change else None
            )
        except Exception:
            return None

    @property
    def regulatory_change_severity(self) -> Optional[str]:
        try:
            rc = self.regulatory_change
            return rc.severity.value if rc and rc.severity else None
        except Exception:
            return None
