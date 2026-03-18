from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow import Workflow
from app.models.case import Case
from app.models.audit_entry import AuditEntry
from app.models.base import WorkflowStatus, AuditAction, ActorType, CaseStatus


WORKFLOW_DEFINITIONS = {
    "pension_review": {
        "name": "Pension Review Workflow",
        "steps": [
            "intake",
            "data_gathering",
            "analysis",
            "recommendation_generation",
            "compliance_review",
            "client_presentation",
            "documentation",
            "completion",
        ],
    },
    "transfer_advice": {
        "name": "Transfer Advice Workflow",
        "steps": [
            "intake",
            "source_pension_analysis",
            "target_comparison",
            "suitability_assessment",
            "recommendation_generation",
            "compliance_review",
            "client_decision",
            "execution",
            "completion",
        ],
    },
    "salary_exchange": {
        "name": "Salary Exchange Workflow",
        "steps": [
            "intake",
            "eligibility_check",
            "calculation",
            "recommendation_generation",
            "compliance_review",
            "employer_approval",
            "documentation",
            "completion",
        ],
    },
}


class FlowService:
    """Workflow orchestration for case lifecycle."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_workflow(
        self,
        case_id: UUID,
        workflow_template: str,
        actor_id: UUID,
    ) -> Workflow:
        """Create a new workflow for a case."""
        if workflow_template not in WORKFLOW_DEFINITIONS:
            raise ValueError(f"Unknown workflow template: {workflow_template}")

        definition = WORKFLOW_DEFINITIONS[workflow_template]
        first_step = definition["steps"][0]

        workflow = Workflow(
            case_id=case_id,
            workflow_template=workflow_template,
            current_step=first_step,
            status=WorkflowStatus.ACTIVE,
            steps_completed=[],
            pending_actions=[
                {
                    "action_name": f"complete_{first_step}",
                    "required_role": "advisor",
                    "description": f"Complete the {first_step} step",
                }
            ],
        )
        self.db.add(workflow)
        await self.db.flush()
        await self.db.refresh(workflow)
        return workflow

    async def complete_step(
        self,
        workflow_id: UUID,
        step_name: str,
        actor_id: UUID,
        organization_id: UUID,
        result: Optional[dict] = None,
    ) -> Workflow:
        """Mark a workflow step as completed and advance to next step."""
        result_query = await self.db.execute(
            select(Workflow)
            .join(Case, Case.id == Workflow.case_id)
            .where(Workflow.id == workflow_id, Case.organization_id == organization_id)
        )
        workflow = result_query.scalar_one_or_none()
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")

        if workflow.current_step != step_name:
            raise ValueError(
                f"Cannot complete step {step_name}, current step is {workflow.current_step}"
            )

        definition = WORKFLOW_DEFINITIONS[workflow.workflow_template]
        steps = definition["steps"]
        current_index = steps.index(step_name)

        # Record step completion
        step_record = {
            "step_name": step_name,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "completed_by": str(actor_id),
            "result": result or {},
        }

        steps_completed = list(workflow.steps_completed) + [step_record]
        workflow.steps_completed = steps_completed

        # Create audit entry
        audit = AuditEntry(
            case_id=workflow.case_id,
            action=AuditAction.WORKFLOW_STEP_COMPLETED,
            actor_id=actor_id,
            actor_type=ActorType.USER,
            details={
                "workflow_id": str(workflow_id),
                "step_name": step_name,
                "result": result,
            },
        )
        self.db.add(audit)

        # Advance to next step or complete workflow
        if current_index + 1 < len(steps):
            next_step = steps[current_index + 1]
            workflow.current_step = next_step
            workflow.pending_actions = [
                {
                    "action_name": f"complete_{next_step}",
                    "required_role": "advisor",
                    "description": f"Complete the {next_step} step",
                }
            ]
        else:
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now(timezone.utc)
            workflow.pending_actions = []

            # Update case status
            case_result = await self.db.execute(
                select(Case).where(Case.id == workflow.case_id)
            )
            case = case_result.scalar_one()
            case.status = CaseStatus.COMPLETED
            case.completed_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(workflow)
        return workflow

    async def get_workflow(
        self, case_id: UUID, organization_id: UUID
    ) -> Optional[Workflow]:
        """Get the active workflow for a case."""
        result = await self.db.execute(
            select(Workflow)
            .join(Case, Case.id == Workflow.case_id)
            .where(Workflow.case_id == case_id, Case.organization_id == organization_id)
            .order_by(Workflow.created_at.desc())
        )
        return result.scalar_one_or_none()

    async def pause_workflow(
        self, workflow_id: UUID, actor_id: UUID, organization_id: UUID, reason: str
    ) -> Workflow:
        """Pause a workflow."""
        result = await self.db.execute(
            select(Workflow)
            .join(Case, Case.id == Workflow.case_id)
            .where(Workflow.id == workflow_id, Case.organization_id == organization_id)
        )
        workflow = result.scalar_one_or_none()
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")

        workflow.status = WorkflowStatus.PAUSED

        audit = AuditEntry(
            case_id=workflow.case_id,
            action=AuditAction.WORKFLOW_PAUSED,
            actor_id=actor_id,
            actor_type=ActorType.USER,
            details={
                "workflow_id": str(workflow_id),
                "reason": reason,
                "paused_at_step": workflow.current_step,
            },
        )
        self.db.add(audit)

        await self.db.flush()
        await self.db.refresh(workflow)
        return workflow

    async def resume_workflow(
        self, workflow_id: UUID, actor_id: UUID, organization_id: UUID
    ) -> Workflow:
        """Resume a paused workflow."""
        result = await self.db.execute(
            select(Workflow)
            .join(Case, Case.id == Workflow.case_id)
            .where(Workflow.id == workflow_id, Case.organization_id == organization_id)
        )
        workflow = result.scalar_one_or_none()
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")

        if workflow.status != WorkflowStatus.PAUSED:
            raise ValueError("Cannot resume workflow that is not paused")

        workflow.status = WorkflowStatus.ACTIVE

        audit = AuditEntry(
            case_id=workflow.case_id,
            action=AuditAction.WORKFLOW_RESUMED,
            actor_id=actor_id,
            actor_type=ActorType.USER,
            details={
                "workflow_id": str(workflow_id),
                "resumed_at_step": workflow.current_step,
            },
        )
        self.db.add(audit)

        await self.db.flush()
        await self.db.refresh(workflow)
        return workflow
