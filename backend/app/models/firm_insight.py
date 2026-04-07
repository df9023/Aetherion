import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import FirmInsightCategory, ValueEnum

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.client_organization import ClientOrganization
    from app.models.case import Case


class FirmInsight(Base):
    __tablename__ = "firm_insights"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # Content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[FirmInsightCategory] = mapped_column(
        ValueEnum(FirmInsightCategory), nullable=False
    )

    # Scoping
    case_types: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    collective_agreements: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    client_organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("client_organizations.id"), nullable=True
    )
    tags: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )

    # Metadata
    source_case_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    upvotes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    upvoted_by: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )

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
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    client_organization: Mapped[Optional["ClientOrganization"]] = relationship(
        "ClientOrganization", foreign_keys=[client_organization_id]
    )
    source_case: Mapped[Optional["Case"]] = relationship(
        "Case", foreign_keys=[source_case_id]
    )

    @property
    def creator_name(self) -> Optional[str]:
        try:
            return self.creator.name if self.creator else None
        except Exception:
            return None

    @property
    def client_organization_name(self) -> Optional[str]:
        try:
            co = self.client_organization
            return co.name if co else None
        except Exception:
            return None

    @property
    def source_case_title(self) -> Optional[str]:
        try:
            sc = self.source_case
            return sc.title if sc else None
        except Exception:
            return None
