from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, computed_field

from app.models.base import CollectiveAgreement
from app.schemas.client import ClientResponse


class ClientOrganizationCreate(BaseModel):
    name: str
    org_number: Optional[str] = None
    industry: Optional[str] = None
    collective_agreement: Optional[CollectiveAgreement] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    employee_count: Optional[int] = None
    notes: Optional[str] = None


class ClientOrganizationUpdate(BaseModel):
    name: Optional[str] = None
    org_number: Optional[str] = None
    industry: Optional[str] = None
    collective_agreement: Optional[CollectiveAgreement] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    employee_count: Optional[int] = None
    notes: Optional[str] = None


class ClientOrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    org_number: Optional[str] = None
    industry: Optional[str] = None
    collective_agreement: Optional[CollectiveAgreement] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    employee_count: Optional[int] = None
    notes: Optional[str] = None
    client_count: int = 0
    created_at: datetime
    updated_at: datetime
    created_by: UUID


class ClientOrganizationDetail(ClientOrganizationResponse):
    """Extended response with full client list for the detail page."""
    clients: list[ClientResponse] = []
