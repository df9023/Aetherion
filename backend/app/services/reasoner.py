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


DOCUMENT_EXTRACTION_TOOL = {
    "name": "extract_document_data",
    "description": "Extract structured pension-relevant data from an uploaded document (pensionsbesked, lönespecifikation, insurance policy, etc.).",
    "input_schema": {
        "type": "object",
        "required": ["document_type", "extracted_fields", "fund_allocations", "other_observations"],
        "properties": {
            "document_type": {
                "type": "string",
                "description": "Identified document type (e.g., 'pensionsbesked', 'lönespecifikation', 'försäkringsbrev', 'årsbesked', 'valcentral').",
            },
            "extracted_fields": {
                "type": "array",
                "description": "All pension-relevant fields extracted from the document.",
                "items": {
                    "type": "object",
                    "required": ["field_name", "value", "confidence"],
                    "properties": {
                        "field_name": {
                            "type": "string",
                            "enum": [
                                "name",
                                "date_of_birth",
                                "employer_name",
                                "collective_agreement",
                                "annual_income",
                                "monthly_income",
                                "employment_status",
                                "pension_provider",
                                "total_fees_percent",
                                "survivor_protection",
                                "pension_capital",
                                "desired_retirement_age",
                                "risk_profile",
                            ],
                            "description": "The field being extracted.",
                        },
                        "value": {
                            "type": "string",
                            "description": "The extracted value as a string.",
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Confidence in the extraction (0.0-1.0). High (>0.8) = clearly stated in document. Medium (0.5-0.8) = inferred or partially visible. Low (<0.5) = uncertain/guessed.",
                        },
                        "source_text": {
                            "type": "string",
                            "description": "The exact text from the document this was extracted from.",
                        },
                    },
                },
            },
            "fund_allocations": {
                "type": "array",
                "description": "Fund allocation details if present in the document.",
                "items": {
                    "type": "object",
                    "required": ["fund_name", "allocation_percent", "confidence"],
                    "properties": {
                        "fund_name": {
                            "type": "string",
                            "description": "Name of the fund.",
                        },
                        "allocation_percent": {
                            "type": "number",
                            "description": "Allocation percentage (0-100).",
                        },
                        "fee_percent": {
                            "type": "number",
                            "description": "Annual fee percentage for this fund, if stated.",
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Confidence in this extraction.",
                        },
                    },
                },
            },
            "other_observations": {
                "type": "string",
                "description": "Free-text observations: anything notable that doesn't fit the structured fields (e.g., special clauses, warnings, pending changes, beneficiary info).",
            },
        },
    },
}


MEETING_BRIEF_TOOL = {
    "name": "generate_meeting_brief",
    "description": "Produce a structured meeting preparation brief for an advisor-client pension meeting.",
    "input_schema": {
        "type": "object",
        "required": [
            "client_overview",
            "pension_situation",
            "key_issues",
            "talking_points",
            "open_questions",
            "meeting_agenda",
        ],
        "properties": {
            "client_overview": {
                "type": "string",
                "description": "Concise summary of the client's situation: age, employment, income, family, risk profile, and relevant background. 2-3 paragraphs.",
            },
            "pension_situation": {
                "type": "array",
                "description": "Breakdown of the client's pension across the three pillars of Swedish pension system.",
                "items": {
                    "type": "object",
                    "required": ["pillar", "description", "estimated_value", "notes"],
                    "properties": {
                        "pillar": {
                            "type": "string",
                            "enum": ["allmän_pension", "tjänstepension", "privat_sparande"],
                            "description": "Which pillar this entry covers.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of current state within this pillar.",
                        },
                        "estimated_value": {
                            "type": "string",
                            "description": "Estimated current or projected value (SEK), or 'Okänt' if unknown.",
                        },
                        "notes": {
                            "type": "string",
                            "description": "Important notes, gaps, or action items for this pillar.",
                        },
                    },
                },
            },
            "key_issues": {
                "type": "array",
                "description": "Issues or risks that should be discussed during the meeting.",
                "items": {
                    "type": "object",
                    "required": ["title", "description", "severity"],
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Short title for the issue.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Explanation of the issue and why it matters.",
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                            "description": "How urgent or impactful this issue is.",
                        },
                    },
                },
            },
            "pre_modeled_scenarios": {
                "type": "array",
                "description": "Pre-calculated scenarios the advisor can present during the meeting.",
                "items": {
                    "type": "object",
                    "required": ["name", "description", "projected_outcome"],
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Scenario name (e.g., 'Nuvarande plan', 'Med löneväxling', 'Tidigarelagd pension').",
                        },
                        "description": {
                            "type": "string",
                            "description": "What this scenario entails.",
                        },
                        "projected_outcome": {
                            "type": "object",
                            "description": "Key-value pairs of projected metrics (e.g., monthly_pension, total_savings, retirement_age).",
                        },
                    },
                },
            },
            "talking_points": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Ordered list of key talking points for the advisor to cover during the meeting.",
            },
            "open_questions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Questions the advisor should ask the client to gather missing information or clarify needs.",
            },
            "meeting_agenda": {
                "type": "array",
                "description": "Suggested meeting agenda with time estimates.",
                "items": {
                    "type": "object",
                    "required": ["topic", "duration_minutes", "description"],
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Agenda item topic.",
                        },
                        "duration_minutes": {
                            "type": "integer",
                            "description": "Suggested time in minutes for this agenda item.",
                        },
                        "description": {
                            "type": "string",
                            "description": "What to cover in this agenda item.",
                        },
                    },
                },
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

    async def generate_meeting_brief(
        self,
        case_id: UUID,
        context: dict,
        knowledge_items: list[dict],
        additional_context: str | None = None,
    ) -> dict:
        """Generate a structured meeting preparation brief. Returns raw dict (no DB model)."""
        template = self.jinja_env.get_template("meeting_brief.j2")
        prompt = template.render(
            context=context,
            knowledge_items=knowledge_items,
            additional_context=additional_context,
        )

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            system=self._render_system_prompt(),
            tools=[MEETING_BRIEF_TOOL],
            tool_choice={"type": "tool", "name": "generate_meeting_brief"},
            messages=[{"role": "user", "content": prompt}],
        )

        return self._extract_tool_input(response, "generate_meeting_brief")

    async def extract_document_data(
        self,
        document_text: str,
        pdf_bytes: bytes | None = None,
    ) -> dict:
        """Extract structured pension data from a document using Claude."""
        template = self.jinja_env.get_template("document_extraction.j2")
        prompt_text = template.render(document_text=document_text)

        # Build message content — use vision if raw PDF bytes provided
        if pdf_bytes:
            import base64
            content = [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": base64.standard_b64encode(pdf_bytes).decode(),
                    },
                },
                {"type": "text", "text": prompt_text},
            ]
        else:
            content = prompt_text

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=self._render_system_prompt(),
            tools=[DOCUMENT_EXTRACTION_TOOL],
            tool_choice={"type": "tool", "name": "extract_document_data"},
            messages=[{"role": "user", "content": content}],
        )

        return self._extract_tool_input(response, "extract_document_data")

    def _extract_tool_input(self, response, tool_name: str) -> dict:
        """Extract the tool input from a Claude tool_use response."""
        for block in response.content:
            if block.type == "tool_use" and block.name == tool_name:
                return block.input
        raise ValueError(
            f"Expected tool_use block for '{tool_name}' not found in response"
        )
