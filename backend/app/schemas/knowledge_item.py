from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.base import KnowledgeCategory


class KnowledgeItemBase(BaseModel):
    title: str
    content: str
    category: KnowledgeCategory
    source: str
    tags: list[str] = []
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None


class KnowledgeItemCreate(KnowledgeItemBase):
    pass


class KnowledgeItemUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[KnowledgeCategory] = None
    source: Optional[str] = None
    tags: Optional[list[str]] = None
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    is_active: Optional[bool] = None


class KnowledgeItemResponse(KnowledgeItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    approved_by: Optional[UUID]


class KnowledgeItemSearch(BaseModel):
    query: str
    category: Optional[KnowledgeCategory] = None
    tags: Optional[list[str]] = None
    limit: int = 10
