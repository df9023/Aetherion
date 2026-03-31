from datetime import datetime
from decimal import Decimal
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.base import RecommendationType, RecommendationStatus


class CitedText(BaseModel):
    text: str
    source_title: Optional[str] = None
    knowledge_item_id: Optional[str] = None


class ReasoningStep(BaseModel):
    step: int
    title: Optional[str] = None
    description: str
    evidence_ids: list[UUID] = []
    cited_texts: list[CitedText] = []
    conclusion: str
    advisor_annotation: Optional[str] = None
    annotated_by: Optional[UUID] = None
    annotated_at: Optional[datetime] = None


class Assumption(BaseModel):
    assumption: str
    basis: str
    impact_if_wrong: str


class Scenario(BaseModel):
    name: str
    description: str
    projected_outcome: dict[str, Any]


class RecommendationBase(BaseModel):
    recommendation_type: RecommendationType
    summary: str
    reasoning_chain: list[ReasoningStep] = []
    assumptions: list[Assumption] = []
    scenarios: Optional[list[Scenario]] = None
    suitability_score: Optional[Decimal] = None


class GenerateRecommendationRequest(BaseModel):
    recommendation_type: Optional[RecommendationType] = None
    additional_context: Optional[str] = None


class RecommendationCreate(RecommendationBase):
    case_id: UUID


class RecommendationUpdate(BaseModel):
    summary: Optional[str] = None
    reasoning_chain: Optional[list[ReasoningStep]] = None
    assumptions: Optional[list[Assumption]] = None
    scenarios: Optional[list[Scenario]] = None
    suitability_score: Optional[Decimal] = None
    status: Optional[RecommendationStatus] = None


class ReasoningMetadata(BaseModel):
    review_status: str = "pending"  # "pending" | "reviewed"
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    review_comment: Optional[str] = None


class AnnotateStepRequest(BaseModel):
    advisor_annotation: str


class ReviewReasoningRequest(BaseModel):
    comment: Optional[str] = None


class RecommendationResponse(RecommendationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    version: int
    status: RecommendationStatus
    reasoning_metadata: Optional[dict[str, Any]] = None
    created_at: datetime
    created_by: UUID
    approved_by: Optional[UUID]
