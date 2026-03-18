from datetime import datetime
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.base import WorkflowStatus


class WorkflowStepCompleted(BaseModel):
    step_name: str
    completed_at: datetime
    completed_by: UUID
    result: dict[str, Any] = {}


class PendingAction(BaseModel):
    action_name: str
    required_role: str
    description: str
    due_date: Optional[datetime] = None


class WorkflowBase(BaseModel):
    workflow_template: str
    current_step: str


class WorkflowCreate(WorkflowBase):
    case_id: UUID


class WorkflowUpdate(BaseModel):
    current_step: Optional[str] = None
    status: Optional[WorkflowStatus] = None
    steps_completed: Optional[list[WorkflowStepCompleted]] = None
    pending_actions: Optional[list[PendingAction]] = None


class WorkflowResponse(WorkflowBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    status: WorkflowStatus
    steps_completed: list[WorkflowStepCompleted]
    pending_actions: list[PendingAction]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
