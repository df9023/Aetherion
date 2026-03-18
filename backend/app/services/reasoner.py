from pathlib import Path
from typing import Optional
from uuid import UUID

from anthropic import AsyncAnthropic
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.recommendation import Recommendation
from app.models.evidence import Evidence
from app.models.base import RecommendationType, EvidenceSourceType
from app.schemas.recommendation import ReasoningStep, Assumption, Scenario


class ReasonerService:
    """LLM reasoning engine for generating structured recommendations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()
        self.client = AsyncAnthropic(api_key=self.settings.anthropic_api_key)
        prompts_dir = Path(__file__).resolve().parent.parent / "prompts"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(prompts_dir)),
            autoescape=False,
        )

    async def generate_recommendation(
        self,
        case_id: UUID,
        recommendation_type: RecommendationType,
        context: dict,
        knowledge_items: list[dict],
        created_by: UUID,
    ) -> Recommendation:
        """Generate a structured recommendation using Claude."""
        template = self.jinja_env.get_template("recommendation.j2")
        prompt = template.render(
            recommendation_type=recommendation_type.value,
            context=context,
            knowledge_items=knowledge_items,
        )

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        # Parse structured output (in production, use tool_use for guaranteed structure)
        parsed = self._parse_recommendation_response(response.content[0].text)

        recommendation = Recommendation(
            case_id=case_id,
            recommendation_type=recommendation_type,
            summary=parsed["summary"],
            reasoning_chain=parsed["reasoning_chain"],
            assumptions=parsed["assumptions"],
            scenarios=parsed.get("scenarios"),
            created_by=created_by,
        )
        self.db.add(recommendation)
        await self.db.flush()

        # Create evidence entries
        for evidence_data in parsed.get("evidences", []):
            evidence = Evidence(
                recommendation_id=recommendation.id,
                source_type=EvidenceSourceType(evidence_data["source_type"]),
                source_reference=evidence_data["source_reference"],
                content_snippet=evidence_data["content_snippet"],
                relevance_explanation=evidence_data["relevance_explanation"],
                confidence=evidence_data["confidence"],
            )
            self.db.add(evidence)

        await self.db.flush()
        await self.db.refresh(recommendation)
        return recommendation

    def _parse_recommendation_response(self, response_text: str) -> dict:
        """Parse LLM response into structured recommendation data.

        In production, this should use Claude's tool_use feature for
        guaranteed structured output.
        """
        # Placeholder implementation - real implementation would parse
        # structured JSON or use tool_use
        return {
            "summary": response_text[:500],
            "reasoning_chain": [],
            "assumptions": [],
            "scenarios": None,
            "evidences": [],
        }

    async def refine_recommendation(
        self,
        recommendation: Recommendation,
        feedback: str,
        user_id: UUID,
    ) -> Recommendation:
        """Refine an existing recommendation based on user feedback."""
        template = self.jinja_env.get_template("refine_recommendation.j2")
        prompt = template.render(
            current_recommendation=recommendation,
            feedback=feedback,
        )

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        parsed = self._parse_recommendation_response(response.content[0].text)

        # Create new version (recommendations are immutable, versioned)
        new_recommendation = Recommendation(
            case_id=recommendation.case_id,
            version=recommendation.version + 1,
            recommendation_type=recommendation.recommendation_type,
            summary=parsed["summary"],
            reasoning_chain=parsed["reasoning_chain"],
            assumptions=parsed["assumptions"],
            scenarios=parsed.get("scenarios"),
            created_by=user_id,
        )
        self.db.add(new_recommendation)
        await self.db.flush()
        await self.db.refresh(new_recommendation)
        return new_recommendation
