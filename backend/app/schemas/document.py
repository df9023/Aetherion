from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.base import DocumentType, FileFormat


class DocumentBase(BaseModel):
    document_type: DocumentType
    title: str
    file_format: FileFormat
    template_id: Optional[str] = None


class DocumentCreate(DocumentBase):
    case_id: UUID
    recommendation_id: Optional[UUID] = None
    file_path: str


class DocumentResponse(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    recommendation_id: Optional[UUID]
    file_path: str
    generated_at: datetime
    generated_by: UUID
    version: int
