import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import DocumentType, FileFormat, ValueEnum

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.recommendation import Recommendation


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False
    )
    recommendation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recommendations.id"), nullable=True
    )
    document_type: Mapped[DocumentType] = mapped_column(
        ValueEnum(DocumentType), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    template_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_format: Mapped[FileFormat] = mapped_column(ValueEnum(FileFormat), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    generated_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="documents")
    recommendation: Mapped[Optional["Recommendation"]] = relationship(
        "Recommendation", back_populates="documents"
    )
