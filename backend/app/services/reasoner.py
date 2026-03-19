import json
from pathlib import Path
from typing import Optional
from uuid import UUID

from anthropic import AsyncAnthropic
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.recommendation import Recommendation
from app.models.evidence import Evidence
from app.models.audit_entry import AuditEntry
from app.models.base import (
    RecommendationType,
    EvidenceSourceType,
    AuditAction,
    ActorType,
)

# Tool definitions for structured output via Claude tool_use

RECOMMENDATION_TOOL = {
    "name": "generate_recommendation",
    "description": "Produce a structured pension recommendation with reasoning chain, assumptions, scenarios, suitability assessment, and evidence citations.",
    "input_schema": {
        "type": "object",
        "required": [
            "summary",
            "reasoning_chain",
            "assumptions",
            "suitability_score",
            "evidences",
            "cost_disclosure",
            "conflict_disclosure",
        ],
        "properties": {
            "summary": {
                "type": "string",
                "description": "Clear, concise summary of the recommendation (2-3 paragraphs). Include what is recommended, why, and expected outcome.",
            },
            "reasoning_chain": {
                "type": "array",
                "description": "Step-by-step reasoning that led to this recommendation.",
                "items": {
                    "type": "object",
                    "required": ["step", "description", "conclusion"],
                    "properties": {
                        "step": {
                            "type": "integer",
                            "description": "Step number, starting at 1.",
                        },
                        "description": {
                            "type": "string",
                            "description": "What was analyzed in this step (behovsanalys, produktjämförelse, lämplighetsbedömning, etc.).",
                        },
                        "evidence_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "UUIDs of knowledge items cited as evidence for this step. Use the IDs from the retrieved knowledge items.",
                        },
                        "conclusion": {
                            "type": "string",
                            "description": "Conclusion drawn from this analysis step.",
                        },
                    },
                },
            },
            "assumptions": {
                "type": "array",
                "description": "All assumptions made during the analysis.",
                "items": {
                    "type": "object",
                    "required": ["assumption", "basis", "impact_if_wrong"],
                    "properties": {
                        "assumption": {
                            "type": "string",
                            "description": "The assumption being made.",
                        },
                        "basis": {
                            "type": "string",
                            "description": "Why this assumption is reasonable (e.g., client data, market convention, regulatory default).",
                        },
                        "impact_if_wrong": {
                            "type": "string",
                            "description": "What changes if this assumption turns out to be incorrect.",
                        },
                    },
                },
            },
            "scenarios": {
                "type": "array",
                "description": "Comparison of different options or outcomes. Include at least a recommended scenario and one alternative.",
                "items": {
                    "type": "object",
                    "required": ["name", "description", "projected_outcome"],
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Scenario name (e.g., 'Rekommenderat alternativ', 'Behålla nuvarande', 'Aggressivare profil').",
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of what this scenario entails.",
                        },
                        "projected_outcome": {
                            "type": "object",
                            "description": "Key-value pairs of projected metrics. Include 'annual_fee' (percent), 'total_cost' (SEK over period), 'projected_monthly_pension' (SEK), and any other relevant metrics.",
                        },
                    },
                },
            },
            "suitability_score": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "Overall suitability score (0.0-1.0). Consider: does the recommendation match the client's risk profile, financial situation, knowledge level, and stated objectives?",
            },
            "evidences": {
                "type": "array",
                "description": "Evidence sources supporting the recommendation.",
                "items": {
                    "type": "object",
                    "required": [
                        "source_type",
                        "source_reference",
                        "content_snippet",
                        "relevance_explanation",
                        "confidence",
                    ],
                    "properties": {
                        "source_type": {
                            "type": "string",
                            "enum": [
                                "product_rule",
                                "regulation",
                                "internal_policy",
                                "market_data",
                                "client_data",
                                "precedent",
                                "expert_knowledge",
                            ],
                            "description": "Type of evidence source.",
                        },
                        "source_reference": {
                            "type": "string",
                            "description": "Reference to the source (knowledge item ID, document name, regulation section, etc.).",
                        },
                        "content_snippet": {
                            "type": "string",
                            "description": "Relevant excerpt from the source.",
                        },
                        "relevance_explanation": {
                            "type": "string",
                            "description": "Why this evidence supports the recommendation.",
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Confidence that this evidence correctly supports the claim (0.0-1.0).",
                        },
                    },
                },
            },
            "cost_disclosure": {
                "type": "string",
                "description": "Summary of all fees and costs associated with the recommendation, including impact on expected returns. Required per IDD.",
            },
            "conflict_disclosure": {
                "type": "string",
                "description": "Disclosure of any conflicts of interest, or explicit statement that none have been identified. Required per IDD.",
            },
        },
    },
}

CLIENT_EXPLANATION_TOOL = {
    "name": "generate_client_explanation",
    "description": "Generate a plain-language explanation of a pension recommendation for the client.",
    "input_schema": {
        "type": "object",
        "required": ["title", "explanation", "key_points", "costs_summary", "next_steps"],
        "properties": {
            "title": {
                "type": "string",
                "description": "Short, descriptive title for the explanation (e.g., 'Din pensionsöversikt och vår rekommendation').",
            },
            "explanation": {
                "type": "string",
                "description": "Full plain-language explanation in Swedish. Use markdown formatting. Cover: current situation, what is recommended, why, risks, and alternatives.",
            },
            "key_points": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3-5 bullet points summarizing the most important takeaways for the client.",
            },
            "costs_summary": {
                "type": "string",
                "description": "Clear explanation of all costs and fees in plain language, with concrete amounts where possible.",
            },
            "next_steps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Ordered list of actions the client needs to take.",
            },
            "risks_and_caveats": {
                "type": "string",
                "description": "Plain-language explanation of risks and what happens if assumptions don't hold.",
            },
        },
    },
}


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

    def _render_system_prompt(self) -> str:
        """Render the system prompt template."""
        template = self.jinja_env.get_template("system.j2")
        return template.render()

    async def generate_recommendation(
        self,
        case_id: UUID,
        recommendation_type: RecommendationType,
        context: dict,
        knowledge_items: list[dict],
        created_by: UUID,
    ) -> Recommendation:
        """Generate a structured recommendation using Claude tool_use."""
        template = self.jinja_env.get_template("recommendation.j2")
        prompt = template.render(
            recommendation_type=recommendation_type.value,
            context=context,
            knowledge_items=knowledge_items,
        )

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            system=self._render_system_prompt(),
            tools=[RECOMMENDATION_TOOL],
            tool_choice={"type": "tool", "name": "generate_recommendation"},
            messages=[{"role": "user", "content": prompt}],
        )

        parsed = self._extract_tool_input(response, "generate_recommendation")

        # Get next version number
        version_result = await self.db.execute(
            select(func.coalesce(func.max(Recommendation.version), 0) + 1).where(
                Recommendation.case_id == case_id
            )
        )
        next_version = version_result.scalar()

        # Build reasoning chain with cost/conflict steps appended
        reasoning_chain = parsed["reasoning_chain"]
        if parsed.get("cost_disclosure"):
            reasoning_chain.append(
                {
                    "step": len(reasoning_chain) + 1,
                    "description": "Kostnadsinformation (IDD-krav)",
                    "evidence_ids": [],
                    "conclusion": parsed["cost_disclosure"],
                }
            )
        if parsed.get("conflict_disclosure"):
            reasoning_chain.append(
                {
                    "step": len(reasoning_chain) + 1,
                    "description": "Intressekonfliktdisklosur (IDD-krav)",
                    "evidence_ids": [],
                    "conclusion": parsed["conflict_disclosure"],
                }
            )

        recommendation = Recommendation(
            case_id=case_id,
            version=next_version,
            recommendation_type=recommendation_type,
            summary=parsed["summary"],
            reasoning_chain=reasoning_chain,
            assumptions=parsed["assumptions"],
            scenarios=parsed.get("scenarios"),
            suitability_score=parsed.get("suitability_score"),
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

        # Audit entry
        audit = AuditEntry(
            case_id=case_id,
            action=AuditAction.RECOMMENDATION_GENERATED,
            actor_id=created_by,
            actor_type=ActorType.SYSTEM,
            details={
                "recommendation_id": str(recommendation.id),
                "recommendation_version": next_version,
                "llm_model": "claude-sonnet-4-20250514",
                "prompt_template": "recommendation.j2",
                "knowledge_items_retrieved": [
                    str(item.get("id", "")) for item in knowledge_items
                ],
            },
        )
        self.db.add(audit)

        await self.db.flush()
        await self.db.refresh(recommendation)
        return recommendation

    async def refine_recommendation(
        self,
        recommendation: Recommendation,
        feedback: str,
        user_id: UUID,
        knowledge_items: list[dict] | None = None,
    ) -> Recommendation:
        """Refine an existing recommendation based on user feedback."""
        template = self.jinja_env.get_template("refine_recommendation.j2")
        prompt = template.render(
            current_recommendation=recommendation,
            feedback=feedback,
            knowledge_items=knowledge_items or [],
        )

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            system=self._render_system_prompt(),
            tools=[RECOMMENDATION_TOOL],
            tool_choice={"type": "tool", "name": "generate_recommendation"},
            messages=[{"role": "user", "content": prompt}],
        )

        parsed = self._extract_tool_input(response, "generate_recommendation")

        reasoning_chain = parsed["reasoning_chain"]
        if parsed.get("cost_disclosure"):
            reasoning_chain.append(
                {
                    "step": len(reasoning_chain) + 1,
                    "description": "Kostnadsinformation (IDD-krav)",
                    "evidence_ids": [],
                    "conclusion": parsed["cost_disclosure"],
                }
            )
        if parsed.get("conflict_disclosure"):
            reasoning_chain.append(
                {
                    "step": len(reasoning_chain) + 1,
                    "description": "Intressekonfliktdisklosur (IDD-krav)",
                    "evidence_ids": [],
                    "conclusion": parsed["conflict_disclosure"],
                }
            )

        new_recommendation = Recommendation(
            case_id=recommendation.case_id,
            version=recommendation.version + 1,
            recommendation_type=recommendation.recommendation_type,
            summary=parsed["summary"],
            reasoning_chain=reasoning_chain,
            assumptions=parsed["assumptions"],
            scenarios=parsed.get("scenarios"),
            suitability_score=parsed.get("suitability_score"),
            created_by=user_id,
        )
        self.db.add(new_recommendation)
        await self.db.flush()

        # Create evidence entries for the new version
        for evidence_data in parsed.get("evidences", []):
            evidence = Evidence(
                recommendation_id=new_recommendation.id,
                source_type=EvidenceSourceType(evidence_data["source_type"]),
                source_reference=evidence_data["source_reference"],
                content_snippet=evidence_data["content_snippet"],
                relevance_explanation=evidence_data["relevance_explanation"],
                confidence=evidence_data["confidence"],
            )
            self.db.add(evidence)

        # Mark previous version as superseded
        from app.models.base import RecommendationStatus

        recommendation.status = RecommendationStatus.SUPERSEDED

        # Audit entry
        audit = AuditEntry(
            case_id=recommendation.case_id,
            action=AuditAction.RECOMMENDATION_EDITED,
            actor_id=user_id,
            actor_type=ActorType.USER,
            details={
                "recommendation_id": str(new_recommendation.id),
                "previous_version": recommendation.version,
                "new_version": recommendation.version + 1,
                "feedback": feedback[:500],
                "llm_model": "claude-sonnet-4-20250514",
                "prompt_template": "refine_recommendation.j2",
            },
        )
        self.db.add(audit)

        await self.db.flush()
        await self.db.refresh(new_recommendation)
        return new_recommendation

    async def generate_client_explanation(
        self,
        recommendation: Recommendation,
        client: dict,
    ) -> dict:
        """Generate a plain-language explanation for the client."""
        # Ensure we have the full recommendation data loaded
        await self.db.refresh(recommendation, ["evidences"])

        template = self.jinja_env.get_template("client_explanation.j2")
        prompt = template.render(
            recommendation={
                "summary": recommendation.summary,
                "reasoning_chain": recommendation.reasoning_chain,
                "assumptions": recommendation.assumptions,
                "scenarios": recommendation.scenarios,
                "suitability_score": (
                    float(recommendation.suitability_score)
                    if recommendation.suitability_score
                    else None
                ),
            },
            client=client,
        )

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=self._render_system_prompt(),
            tools=[CLIENT_EXPLANATION_TOOL],
            tool_choice={"type": "tool", "name": "generate_client_explanation"},
            messages=[{"role": "user", "content": prompt}],
        )

        return self._extract_tool_input(response, "generate_client_explanation")

    def _extract_tool_input(self, response, tool_name: str) -> dict:
        """Extract the tool input from a Claude tool_use response."""
        for block in response.content:
            if block.type == "tool_use" and block.name == tool_name:
                return block.input
        raise ValueError(
            f"Expected tool_use block for '{tool_name}' not found in response"
        )
