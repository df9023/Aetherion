from datetime import datetime
from decimal import Decimal
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.base import RecommendationType, RecommendationStatus


class ReasoningStep(BaseModel):
    step: int
    description: str
    evidence_ids: list[UUID] = []
    conclusion: str


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


class RecommendationCreate(RecommendationBase):
    case_id: UUID


class RecommendationUpdate(BaseModel):
    summary: Optional[str] = None
    reasoning_chain: Optional[list[ReasoningStep]] = None
    assumptions: Optional[list[Assumption]] = None
    scenarios: Optional[list[Scenario]] = None
    suitability_score: Optional[Decimal] = None
    status: Optional[RecommendationStatus] = None


class RecommendationResponse(RecommendationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    version: int
    status: RecommendationStatus
    created_at: datetime
    created_by: UUID
    approved_by: Optional[UUID]
