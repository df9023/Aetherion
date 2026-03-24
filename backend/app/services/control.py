from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recommendation import Recommendation
from app.models.audit_entry import AuditEntry
from app.models.base import (
    AuditAction,
    ActorType,
)


class ComplianceCheckResult:
    """Result of a compliance check."""

    def __init__(
        self,
        passed: bool,
        check_name: str,
        message: str,
        details: Optional[dict] = None,
    ):
        self.passed = passed
        self.check_name = check_name
        self.message = message
        self.details = details or {}


class ControlService:
    """Compliance checks and audit trail management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_compliance_checks(
        self,
        recommendation: Recommendation,
        actor_id: UUID,
    ) -> list[ComplianceCheckResult]:
        """Run all compliance checks on a recommendation.

        MVP checks per COMPLIANCE_SPEC.md:
        1. Completeness (reasoning + assumptions present)
        2. Suitability alignment (score meets threshold)
        3. Evidence coverage (at least 1 source)
        4. Cost disclosure present
        5. Conflict disclosure present
        """
        results = []

        results.append(await self._check_completeness(recommendation))
        results.append(await self._check_suitability_score(recommendation))
        results.append(await self._check_evidence_coverage(recommendation))
        results.append(await self._check_cost_disclosure(recommendation))
        results.append(await self._check_conflict_disclosure(recommendation))

        # Record audit entries for each check
        for result in results:
            action = (
                AuditAction.COMPLIANCE_CHECK_PASSED
                if result.passed
                else AuditAction.COMPLIANCE_CHECK_FAILED
            )
            audit = AuditEntry(
                case_id=recommendation.case_id,
                action=action,
                actor_id=actor_id,
                actor_type=ActorType.SYSTEM,
                details={
                    "check_name": result.check_name,
                    "passed": result.passed,
                    "message": result.message,
                    **result.details,
                },
            )
            self.db.add(audit)

        await self.db.flush()
        return results

    async def _check_completeness(
        self, recommendation: Recommendation
    ) -> ComplianceCheckResult:
        """Check that all required sections of the recommendation are populated."""
        missing = []
        if not recommendation.summary:
            missing.append("summary")
        if not recommendation.reasoning_chain:
            missing.append("reasoning_chain")
        if not recommendation.assumptions:
            missing.append("assumptions")

        passed = len(missing) == 0
        return ComplianceCheckResult(
            passed=passed,
            check_name="completeness",
            message=(
                "All required recommendation sections are populated"
                if passed
                else f"Missing required sections: {', '.join(missing)}"
            ),
            details={"missing_sections": missing},
        )

    async def _check_suitability_score(
        self, recommendation: Recommendation
    ) -> ComplianceCheckResult:
        """Check that suitability score meets minimum threshold."""
        min_score = 0.7
        score = recommendation.suitability_score

        if score is None:
            return ComplianceCheckResult(
                passed=False,
                check_name="suitability_score",
                message="Suitability score not calculated",
            )

        passed = float(score) >= min_score
        return ComplianceCheckResult(
            passed=passed,
            check_name="suitability_score",
            message=(
                f"Suitability score {score} meets threshold"
                if passed
                else f"Suitability score {score} below threshold {min_score}"
            ),
            details={"score": float(score), "threshold": min_score},
        )

    async def _check_evidence_coverage(
        self, recommendation: Recommendation
    ) -> ComplianceCheckResult:
        """Check that recommendation has at least one evidence source cited."""
        await self.db.refresh(recommendation, ["evidences"])
        evidence_count = len(recommendation.evidences)
        min_evidence = 1

        passed = evidence_count >= min_evidence
        return ComplianceCheckResult(
            passed=passed,
            check_name="evidence_coverage",
            message=(
                f"Recommendation has {evidence_count} pieces of evidence"
                if passed
                else f"Recommendation needs at least {min_evidence} piece of evidence"
            ),
            details={"count": evidence_count, "minimum": min_evidence},
        )

    async def _check_cost_disclosure(
        self, recommendation: Recommendation
    ) -> ComplianceCheckResult:
        """Check that cost/fee information is included in the recommendation."""
        has_cost_info = False
        if recommendation.scenarios:
            for scenario in recommendation.scenarios:
                scenario_data = scenario if isinstance(scenario, dict) else {}
                outcome = scenario_data.get("projected_outcome", {})
                if any(
                    k in outcome
                    for k in ("fees", "costs", "total_cost", "annual_fee", "avgift")
                ):
                    has_cost_info = True
                    break

        if not has_cost_info and recommendation.reasoning_chain:
            for step in recommendation.reasoning_chain:
                step_data = step if isinstance(step, dict) else {}
                desc = step_data.get("description", "").lower()
                conclusion = step_data.get("conclusion", "").lower()
                if any(
                    term in desc or term in conclusion
                    for term in ("cost", "fee", "avgift", "kostnad")
                ):
                    has_cost_info = True
                    break

        return ComplianceCheckResult(
            passed=has_cost_info,
            check_name="cost_disclosure",
            message=(
                "Cost disclosure information is present"
                if has_cost_info
                else "Missing cost/fee disclosure — required per IDD regulations"
            ),
        )

    async def _check_conflict_disclosure(
        self, recommendation: Recommendation
    ) -> ComplianceCheckResult:
        """Check that conflict of interest disclosure is addressed."""
        has_conflict_info = False
        if recommendation.reasoning_chain:
            for step in recommendation.reasoning_chain:
                step_data = step if isinstance(step, dict) else {}
                desc = step_data.get("description", "").lower()
                conclusion = step_data.get("conclusion", "").lower()
                if any(
                    term in desc or term in conclusion
                    for term in (
                        "conflict of interest",
                        "intressekonflikt",
                        "conflict",
                    )
                ):
                    has_conflict_info = True
                    break

        if not has_conflict_info and recommendation.assumptions:
            for assumption in recommendation.assumptions:
                assumption_data = assumption if isinstance(assumption, dict) else {}
                text = assumption_data.get("assumption", "").lower()
                if any(
                    term in text
                    for term in (
                        "conflict of interest",
                        "intressekonflikt",
                        "no conflict",
                    )
                ):
                    has_conflict_info = True
                    break

        return ComplianceCheckResult(
            passed=has_conflict_info,
            check_name="conflict_disclosure",
            message=(
                "Conflict of interest disclosure is present"
                if has_conflict_info
                else "Missing conflict of interest disclosure — required per IDD regulations"
            ),
        )

    async def create_audit_entry(
        self,
        case_id: UUID,
        action: AuditAction,
        actor_id: UUID,
        actor_type: ActorType,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
    ) -> AuditEntry:
        """Create an audit trail entry."""
        audit = AuditEntry(
            case_id=case_id,
            action=action,
            actor_id=actor_id,
            actor_type=actor_type,
            details=details or {},
            ip_address=ip_address,
        )
        self.db.add(audit)
        await self.db.flush()
        await self.db.refresh(audit)
        return audit

    async def get_audit_trail(
        self,
        case_id: UUID,
        action_filter: Optional[AuditAction] = None,
    ) -> list[AuditEntry]:
        """Retrieve audit trail for a case."""
        query = select(AuditEntry).where(AuditEntry.case_id == case_id)
        if action_filter:
            query = query.where(AuditEntry.action == action_filter)
        query = query.order_by(AuditEntry.timestamp.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())
