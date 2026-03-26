import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from decimal import Decimal

from sqlalchemy import Boolean, Integer, String, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import EvidenceSourceType, ValueEnum

if TYPE_CHECKING:
    from app.models.recommendation import Recommendation
    from app.models.knowledge_item import KnowledgeItem


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

    # Native citation fields (from Claude Citations API)
    cited_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    document_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    start_char_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    end_char_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    knowledge_item_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("knowledge_items.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    recommendation: Mapped["Recommendation"] = relationship(
        "Recommendation", back_populates="evidences"
    )
    knowledge_item: Mapped[Optional["KnowledgeItem"]] = relationship(
        "KnowledgeItem", lazy="selectin",
    )
