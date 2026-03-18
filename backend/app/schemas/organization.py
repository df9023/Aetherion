from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.base import OrganizationType


class OrganizationBase(BaseModel):
    name: str
    org_type: OrganizationType
    jurisdiction: str = "SE"
    settings: dict = {}


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    org_type: Optional[OrganizationType] = None
    jurisdiction: Optional[str] = None
    settings: Optional[dict] = None
    is_active: Optional[bool] = None


class OrganizationResponse(OrganizationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    is_active: bool
