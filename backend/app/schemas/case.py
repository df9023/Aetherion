from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.base import CaseType, CaseStatus


class CaseBase(BaseModel):
    title: str
    case_type: CaseType
    summary: Optional[str] = None
    meeting_date: Optional[datetime] = None


class CaseCreate(CaseBase):
    client_id: UUID
    assigned_to: UUID


class CaseUpdate(BaseModel):
    title: Optional[str] = None
    case_type: Optional[CaseType] = None
    status: Optional[CaseStatus] = None
    summary: Optional[str] = None
    meeting_date: Optional[datetime] = None
    assigned_to: Optional[UUID] = None


class CaseResponse(CaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    client_id: UUID
    assigned_to: UUID
    status: CaseStatus
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    organization_id: UUID
