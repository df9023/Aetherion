from datetime import datetime
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.base import AuditAction, ActorType


class AuditEntryBase(BaseModel):
    action: AuditAction
    actor_id: UUID
    actor_type: ActorType
    details: dict[str, Any] = {}
    ip_address: Optional[str] = None


class AuditEntryCreate(AuditEntryBase):
    case_id: UUID


class AuditEntryResponse(AuditEntryBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    timestamp: datetime
