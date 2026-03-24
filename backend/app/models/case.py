import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import CaseType, CaseStatus, ValueEnum

if TYPE_CHECKING:
    from app.models.client import Client
    from app.models.user import User
    from app.models.recommendation import Recommendation
    from app.models.audit_entry import AuditEntry
    from app.models.document import Document
    from app.models.workflow import Workflow


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False
    )
    assigned_to: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    case_type: Mapped[CaseType] = mapped_column(ValueEnum(CaseType), nullable=False)
    status: Mapped[CaseStatus] = mapped_column(
        ValueEnum(CaseStatus), nullable=False, default=CaseStatus.DRAFT
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meeting_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
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
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )

    # Relationships
    client: Mapped["Client"] = relationship("Client", back_populates="cases")
    assigned_user: Mapped["User"] = relationship(
        "User", back_populates="assigned_cases", foreign_keys=[assigned_to]
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation", back_populates="case"
    )
    audit_entries: Mapped[list["AuditEntry"]] = relationship(
        "AuditEntry", back_populates="case"
    )
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="case")
    workflows: Mapped[list["Workflow"]] = relationship("Workflow", back_populates="case")
