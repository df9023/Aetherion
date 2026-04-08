import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import RegulatoryChangeSeverity, ValueEnum

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.knowledge_item import KnowledgeItem
    from app.models.case_impact import CaseImpact


class RegulatoryChange(Base):
    __tablename__ = "regulatory_changes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    severity: Mapped[RegulatoryChangeSeverity] = mapped_column(
        ValueEnum(RegulatoryChangeSeverity), nullable=False
    )

    # Scoping — who does this change affect?
    affected_case_types: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    affected_agreements: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    affected_tags: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )

    # Optional link to the regulatory document in the knowledge base
    knowledge_item_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("knowledge_items.id"), nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
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
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])
    knowledge_item: Mapped[Optional["KnowledgeItem"]] = relationship(
        "KnowledgeItem", foreign_keys=[knowledge_item_id]
    )
    case_impacts: Mapped[list["CaseImpact"]] = relationship(
        "CaseImpact", back_populates="regulatory_change", cascade="all, delete-orphan"
    )

    @property
    def creator_name(self) -> Optional[str]:
        try:
            return self.creator.name if self.creator else None
        except Exception:
            return None

    @property
    def knowledge_item_title(self) -> Optional[str]:
        try:
            ki = self.knowledge_item
            return ki.title if ki else None
        except Exception:
            return None
