import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import OrganizationType

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.knowledge_item import KnowledgeItem


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    org_type: Mapped[OrganizationType] = mapped_column(
        Enum(OrganizationType), nullable=False
    )
    jurisdiction: Mapped[str] = mapped_column(String(10), nullable=False, default="SE")
    settings: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="organization")
    knowledge_items: Mapped[list["KnowledgeItem"]] = relationship(
        "KnowledgeItem", back_populates="organization"
    )
