from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.base import FirmInsightCategory


class FirmInsightBase(BaseModel):
    title: str = Field(..., max_length=255)
    content: str
    category: FirmInsightCategory
    case_types: list[str] = []
    collective_agreements: list[str] = []
    client_organization_id: Optional[UUID] = None
    tags: list[str] = []
    source_case_id: Optional[UUID] = None


class FirmInsightCreate(FirmInsightBase):
    pass


class FirmInsightUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    category: Optional[FirmInsightCategory] = None
    case_types: Optional[list[str]] = None
    collective_agreements: Optional[list[str]] = None
    client_organization_id: Optional[UUID] = None
    tags: Optional[list[str]] = None
    is_active: Optional[bool] = None


class FirmInsightResponse(FirmInsightBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    created_by: UUID
    creator_name: Optional[str] = None
    client_organization_name: Optional[str] = None
    source_case_title: Optional[str] = None
    is_active: bool
    upvotes: int
    created_at: datetime
    updated_at: datetime
