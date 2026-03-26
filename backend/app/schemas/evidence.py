from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.base import EvidenceSourceType


class EvidenceBase(BaseModel):
    source_type: EvidenceSourceType
    source_reference: str
    content_snippet: str
    relevance_explanation: str
    confidence: Decimal = Field(ge=0, le=1)


class EvidenceCreate(EvidenceBase):
    recommendation_id: UUID


class EvidenceResponse(EvidenceBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recommendation_id: UUID
    verified: bool = True
    verification_status: str = "verified"

    # Native citation fields
    cited_text: str | None = None
    document_index: int | None = None
    start_char_index: int | None = None
    end_char_index: int | None = None
    knowledge_item_id: UUID | None = None

    created_at: datetime
