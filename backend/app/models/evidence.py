import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from decimal import Decimal

from sqlalchemy import Boolean, String, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import EvidenceSourceType, ValueEnum

if TYPE_CHECKING:
    from app.models.recommendation import Recommendation


class Evidence(Base):
    __tablename__ = "evidences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    recommendation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recommendations.id"), nullable=False
    )
    source_type: Mapped[EvidenceSourceType] = mapped_column(
        ValueEnum(EvidenceSourceType), nullable=False
    )
    source_reference: Mapped[str] = mapped_column(String(1024), nullable=False)
    content_snippet: Mapped[str] = mapped_column(Text, nullable=False)
    relevance_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    verification_status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="verified"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    # Relationships
    recommendation: Mapped["Recommendation"] = relationship(
        "Recommendation", back_populates="evidences"
    )
