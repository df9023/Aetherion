import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import UserRole, ValueEnum

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.case import Case
    from app.models.client import Client


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(ValueEnum(UserRole), nullable=False)
    workos_user_id: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="users"
    )
    assigned_cases: Mapped[list["Case"]] = relationship(
        "Case", back_populates="assigned_user", foreign_keys="Case.assigned_to"
    )
    created_clients: Mapped[list["Client"]] = relationship(
        "Client", back_populates="creator"
    )
