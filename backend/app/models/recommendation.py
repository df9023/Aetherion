import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from decimal import Decimal

from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import RecommendationType, RecommendationStatus, ValueEnum

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.user import User
    from app.models.evidence import Evidence
    from app.models.document import Document


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    recommendation_type: Mapped[RecommendationType] = mapped_column(
        ValueEnum(RecommendationType), nullable=False
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    reasoning_chain: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)
    assumptions: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)
    scenarios: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    suitability_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    status: Mapped[RecommendationStatus] = mapped_column(
        ValueEnum(RecommendationStatus), nullable=False, default=RecommendationStatus.DRAFT
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="recommendations")
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    approver: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by])
    evidences: Mapped[list["Evidence"]] = relationship(
        "Evidence", back_populates="recommendation"
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="recommendation"
    )
