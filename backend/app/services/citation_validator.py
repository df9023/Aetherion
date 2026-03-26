import logging
import re
from dataclasses import dataclass, field
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge_item import KnowledgeItem

logger = logging.getLogger(__name__)

UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)


@dataclass
class ValidatedEvidence:
    original: dict
    verified: bool
    verification_status: str  # "verified", "partially_verified", "unverified"
    matched_knowledge_item_id: str | None
    overlap_score: float


@dataclass
class ValidationResult:
    evidences: list[ValidatedEvidence]
    reasoning_chain: list[dict]
    warnings: list[str] = field(default_factory=list)
    citation_score: float = 0.0


def _longest_common_substring_length(a: str, b: str) -> int:
    """Compute the length of the longest common substring between *a* and *b*.

    Uses a memory-efficient rolling-row DP approach.  For the sizes we deal
    with (snippet ≤ few hundred chars, source ≤ few thousand) this is fast.
    """
    if not a or not b:
        return 0
    # Normalise for comparison
    a = a.lower().strip()
    b = b.lower().strip()
    m, n = len(a), len(b)
    prev = [0] * (n + 1)
    best = 0
    for i in range(1, m + 1):
        curr = [0] * (n + 1)
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                curr[j] = prev[j - 1] + 1
                if curr[j] > best:
                    best = curr[j]
        prev = curr
    return best


def _compute_overlap_score(snippet: str, source_content: str) -> float:
    """Return 0.0-1.0 indicating how much of *snippet* appears in *source_content*."""
    if not snippet:
        return 0.0
    lcs_len = _longest_common_substring_length(snippet, source_content)
    return lcs_len / len(snippet.strip())


class CitationValidator:
    """Post-processing validator for LLM-generated citations.

    Runs after Claude produces a recommendation and before it is persisted.
    Does NOT call the LLM — all checks are deterministic.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def validate_recommendation(
        self,
        parsed_output: dict,
        retrieved_knowledge: list[dict],
        organization_id: UUID,
    ) -> ValidationResult:
        warnings: list[str] = []

        # Build lookup of retrieved knowledge items (passed to Claude)
        retrieved_by_id: dict[str, dict] = {
            str(ki.get("id", "")): ki for ki in retrieved_knowledge
        }

        # ------------------------------------------------------------------
        # 1 & 2 & 3  — Validate each evidence item
        # ------------------------------------------------------------------
        validated_evidences: list[ValidatedEvidence] = []

        for ev_data in parsed_output.get("evidences", []):
            source_ref = ev_data.get("source_reference", "")
            snippet = ev_data.get("content_snippet", "")
            is_uuid = bool(UUID_PATTERN.match(source_ref))

            matched_id: str | None = None
            overlap = 0.0
            status = "unverified"

            if is_uuid:
                # Check if it was in the retrieved set
                if source_ref in retrieved_by_id:
                    matched_id = source_ref
                    source_content = retrieved_by_id[source_ref].get("content", "")
                    overlap = _compute_overlap_score(snippet, source_content)
                else:
                    # Not in retrieved set — check DB as fallback
                    try:
                        result = await self.db.execute(
                            select(KnowledgeItem).where(
                                KnowledgeItem.id == UUID(source_ref),
                                KnowledgeItem.organization_id == organization_id,
                            )
                        )
                        ki = result.scalar_one_or_none()
                        if ki:
                            matched_id = source_ref
                            overlap = _compute_overlap_score(snippet, ki.content)
                            warnings.append(
                                f"Evidence references knowledge item {source_ref} "
                                f"which was not in the retrieved set but exists in DB."
                            )
                        else:
                            warnings.append(
                                f"Evidence references non-existent knowledge item {source_ref}."
                            )
                    except (ValueError, Exception):
                        warnings.append(
                            f"Evidence has invalid UUID source_reference: {source_ref}."
                        )
            else:
                # Non-UUID reference (regulation name, expert knowledge, etc.)
                # These can't be verified against the knowledge base
                # Mark as partially_verified if they at least cite something specific
                if len(source_ref) > 3:
                    status = "partially_verified"
                    overlap = 0.5  # nominal

            # Determine verification status from overlap score
            if matched_id:
                if overlap > 0.6:
                    status = "verified"
                elif overlap > 0.3:
                    status = "partially_verified"
                    warnings.append(
                        f"Evidence for {source_ref}: snippet is paraphrased "
                        f"(overlap {overlap:.0%}). Original text differs."
                    )
                else:
                    status = "unverified"
                    warnings.append(
                        f"Evidence for {source_ref}: snippet could not be matched "
                        f"to source content (overlap {overlap:.0%}). "
                        f"Possible hallucination."
                    )

            validated_evidences.append(ValidatedEvidence(
                original=ev_data,
                verified=(status == "verified"),
                verification_status=status,
                matched_knowledge_item_id=matched_id,
                overlap_score=overlap,
            ))

        # ------------------------------------------------------------------
        # 4 — Clean reasoning chain evidence_ids
        # ------------------------------------------------------------------
        # Build set of all valid evidence source_references
        valid_refs = {
            ve.matched_knowledge_item_id
            for ve in validated_evidences
            if ve.verification_status in ("verified", "partially_verified")
            and ve.matched_knowledge_item_id
        }
        # Also include non-UUID refs that are at least partially verified
        valid_non_uuid_refs = {
            ve.original.get("source_reference", "")
            for ve in validated_evidences
            if ve.verification_status in ("verified", "partially_verified")
            and not ve.matched_knowledge_item_id
        }

        cleaned_chain = []
        for step in parsed_output.get("reasoning_chain", []):
            evidence_ids = step.get("evidence_ids", [])
            # Keep only IDs that exist in the retrieved knowledge
            cleaned_ids = [
                eid for eid in evidence_ids
                if eid in retrieved_by_id or eid in valid_refs
            ]
            if evidence_ids and not cleaned_ids:
                warnings.append(
                    f"Reasoning step {step.get('step', '?')}: "
                    f"all {len(evidence_ids)} evidence references were invalid and removed."
                )
            cleaned_step = {**step, "evidence_ids": cleaned_ids}
            cleaned_chain.append(cleaned_step)

        # ------------------------------------------------------------------
        # Compute citation score
        # ------------------------------------------------------------------
        total = len(validated_evidences)
        if total > 0:
            verified_count = sum(
                1 for ve in validated_evidences
                if ve.verification_status in ("verified", "partially_verified")
            )
            citation_score = verified_count / total
        else:
            citation_score = 1.0  # No citations to validate

        if citation_score < 0.5:
            warnings.append(
                f"Low citation score ({citation_score:.0%}): "
                f"most citations could not be verified against the knowledge base."
            )

        return ValidationResult(
            evidences=validated_evidences,
            reasoning_chain=cleaned_chain,
            warnings=warnings,
            citation_score=citation_score,
        )
