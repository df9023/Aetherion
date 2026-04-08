import uuid
from datetime import datetime, date, timezone
from typing import TYPE_CHECKING, Optional
from decimal import Decimal

from sqlalchemy import String, Date, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import EmploymentStatus, CollectiveAgreement, RiskProfile, ValueEnum
from app.utils.encryption import EncryptedString

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.case import Case
    from app.models.organization import Organization
    from app.models.client_organization import ClientOrganization


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    external_id: Mapped[Optional[str]] = mapped_column(EncryptedString(512), nullable=True)
    name: Mapped[str] = mapped_column(EncryptedString(512), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    employment_status: Mapped[EmploymentStatus] = mapped_column(
        ValueEnum(EmploymentStatus), nullable=False
    )
    employer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    collective_agreement: Mapped[CollectiveAgreement] = mapped_column(
        ValueEnum(CollectiveAgreement), nullable=False
    )
    annual_income: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    desired_retirement_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    risk_profile: Mapped[Optional[RiskProfile]] = mapped_column(
        ValueEnum(RiskProfile), nullable=True
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
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    client_organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("client_organizations.id"), nullable=True
    )

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    creator: Mapped["User"] = relationship("User", back_populates="created_clients")
    cases: Mapped[list["Case"]] = relationship("Case", back_populates="client")
    client_organization: Mapped[Optional["ClientOrganization"]] = relationship(
        "ClientOrganization", back_populates="clients"
    )

    @property
    def client_organization_name(self) -> Optional[str]:
        """Resolve org name from eagerly-loaded relationship."""
        try:
            co = self.client_organization
            return co.name if co else None
        except Exception:
            return None
