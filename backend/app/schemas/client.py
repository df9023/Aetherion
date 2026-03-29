from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.base import EmploymentStatus, CollectiveAgreement, RiskProfile


class ClientBase(BaseModel):
    name: str
    date_of_birth: date
    employment_status: EmploymentStatus
    collective_agreement: CollectiveAgreement
    external_id: Optional[str] = None
    employer_name: Optional[str] = None
    annual_income: Optional[Decimal] = None
    desired_retirement_age: Optional[int] = None
    risk_profile: Optional[RiskProfile] = None


class ClientCreate(ClientBase):
    client_organization_id: Optional[UUID] = None


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    date_of_birth: Optional[date] = None
    employment_status: Optional[EmploymentStatus] = None
    collective_agreement: Optional[CollectiveAgreement] = None
    external_id: Optional[str] = None
    employer_name: Optional[str] = None
    annual_income: Optional[Decimal] = None
    desired_retirement_age: Optional[int] = None
    risk_profile: Optional[RiskProfile] = None
    client_organization_id: Optional[UUID] = None


class ClientResponse(ClientBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    client_organization_id: Optional[UUID] = None
    client_organization_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: UUID
