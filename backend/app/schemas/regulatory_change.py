from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.base import CaseImpactStatus, RegulatoryChangeSeverity


class RegulatoryChangeBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str
    source: str = Field(..., max_length=255)
    source_url: Optional[str] = Field(None, max_length=1024)
    severity: RegulatoryChangeSeverity
    affected_case_types: list[str] = []
    affected_agreements: list[str] = []
    affected_tags: list[str] = []
    knowledge_item_id: Optional[UUID] = None
    published_at: Optional[datetime] = None


class RegulatoryChangeCreate(RegulatoryChangeBase):
    pass


class RegulatoryChangeUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    source: Optional[str] = Field(None, max_length=255)
    source_url: Optional[str] = Field(None, max_length=1024)
    severity: Optional[RegulatoryChangeSeverity] = None
    affected_case_types: Optional[list[str]] = None
    affected_agreements: Optional[list[str]] = None
    affected_tags: Optional[list[str]] = None
    knowledge_item_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class RegulatoryChangeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    created_by: Optional[UUID] = None
    creator_name: Optional[str] = None
    title: str
    description: str
    source: str
    source_url: Optional[str] = None
    severity: RegulatoryChangeSeverity
    affected_case_types: list[str]
    affected_agreements: list[str]
    affected_tags: list[str]
    knowledge_item_id: Optional[UUID] = None
    knowledge_item_title: Optional[str] = None
    is_active: bool
    published_at: datetime
    created_at: datetime
    updated_at: datetime
    impact_count: Optional[int] = None
    open_impact_count: Optional[int] = None


class CaseImpactResolve(BaseModel):
    resolution_note: Optional[str] = None


class CaseImpactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    regulatory_change_id: UUID
    regulatory_change_title: Optional[str] = None
    regulatory_change_severity: Optional[str] = None
    case_id: UUID
    case_title: Optional[str] = None
    case_status: Optional[str] = None
    match_reason: str
    affected_sections: list[str]
    status: CaseImpactStatus
    resolved_by: Optional[UUID] = None
    resolver_name: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_note: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ScanResult(BaseModel):
    regulatory_change_id: UUID
    new_impacts: int
    skipped_existing: int
    total_matched_cases: int
    impacts: list[CaseImpactResponse]


class ComplianceHealthResponse(BaseModel):
    total_active_cases: int
    cases_with_open_impacts: int
    total_open_impacts: int
    impacts_by_severity: dict[str, int]
    recent_changes: list[RegulatoryChangeResponse]
