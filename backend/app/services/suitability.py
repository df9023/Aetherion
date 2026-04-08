"""Deterministic suitability scoring engine.

Replaces the LLM-generated suitability_score with a weighted scoring system
based on objective client data. Each factor is scored 0.0–1.0, multiplied by
its weight, and summed to produce the total score.

The engine is designed to be transparent: every factor includes its score,
weight, and a short reason so that advisors can verify the assessment.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Factor weights — must sum to 1.0
# ---------------------------------------------------------------------------

FACTOR_WEIGHTS: dict[str, float] = {
    "risk_profile_match": 0.25,
    "age_appropriateness": 0.20,
    "income_adequacy": 0.15,
    "agreement_eligibility": 0.20,
    "data_completeness": 0.20,
}

# Risk level ordering for scenario comparison
RISK_LEVELS: dict[str, int] = {
    "low": 1,
    "moderate": 2,
    "medium": 2,
    "high": 3,
    "aggressive": 4,
    "conservative": 1,
    "balanced": 2,
}

# Agreements compatible with salary exchange
SALARY_EXCHANGE_AGREEMENTS: set[str] = {"ITP1", "ITP2", "SAF_LO", "KAP_KL", "AKAP_KL"}

# All known collective agreements
KNOWN_AGREEMENTS: set[str] = {"ITP1", "ITP2", "SAF_LO", "KAP_KL", "AKAP_KL", "PA16"}

# Completeness fields to check (matches the client dict keys from the API context)
COMPLETENESS_FIELDS: list[str] = [
    "name",
    "date_of_birth",
    "employer_name",
    "collective_agreement",
    "annual_income",
    "risk_profile",
    "desired_retirement_age",
]

# Minimum income for salary exchange to be considered adequate
SALARY_EXCHANGE_MIN_INCOME: float = 300_000.0


# ---------------------------------------------------------------------------
# Pydantic output models
# ---------------------------------------------------------------------------


class SuitabilityFactor(BaseModel):
    """A single scored factor in the suitability assessment."""

    name: str = Field(description="Factor name")
    score: float = Field(ge=0.0, le=1.0, description="Factor score (0.0–1.0)")
    weight: float = Field(description="Factor weight in total score")
    reason: str = Field(description="Short explanation of the score")


class SuitabilityResult(BaseModel):
    """Complete suitability assessment with factor breakdown."""

    total_score: float = Field(ge=0.0, le=1.0, description="Weighted total score (0.0–1.0)")
    factors: list[SuitabilityFactor] = Field(description="Individual factor scores")
    grade: str = Field(description="Overall grade: 'high', 'moderate', or 'low'")


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class SuitabilityEngine:
    """Deterministic weighted scoring system for recommendation suitability.

    Scores five factors:
    1. Risk profile match (0.25) — client risk profile vs scenario risk levels
    2. Age appropriateness (0.20) — years to retirement vs recommendation type
    3. Income adequacy (0.15) — affordability of costs/contributions
    4. Agreement eligibility (0.20) — agreement compatibility with recommendation type
    5. Data completeness (0.20) — how many client fields are filled
    """

    def _parse_dob(self, client: dict) -> date | None:
        raw = client.get("date_of_birth")
        if raw is None:
            return None
        if isinstance(raw, date):
            return raw
        try:
            return datetime.strptime(str(raw), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    def _client_age(self, client: dict) -> int | None:
        dob = self._parse_dob(client)
        if dob is None:
            return None
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def _parse_income(self, client: dict) -> float | None:
        raw = client.get("annual_income")
        if raw is None:
            return None
        try:
            return float(raw)
        except (ValueError, TypeError):
            return None

    def _score_risk_profile_match(
        self, client: dict, scenarios: list[dict] | None
    ) -> SuitabilityFactor:
        """Score how well the recommendation's risk level matches the client's profile.

        Full score if aligned, partial if moderate mismatch, low if aggressive
        recommendation for low-risk client or vice versa.
        """
        risk_profile = client.get("risk_profile")

        if not risk_profile:
            return SuitabilityFactor(
                name="risk_profile_match",
                score=0.5,
                weight=FACTOR_WEIGHTS["risk_profile_match"],
                reason="Riskprofil saknas — kan inte bedöma matchning.",
            )

        if not scenarios:
            return SuitabilityFactor(
                name="risk_profile_match",
                score=0.5,
                weight=FACTOR_WEIGHTS["risk_profile_match"],
                reason="Inga scenarier att jämföra mot riskprofilen.",
            )

        client_risk_level = RISK_LEVELS.get(risk_profile.lower(), 2)

        # Extract risk indicators from scenarios
        scenario_risk_levels: list[int] = []
        for scenario in scenarios:
            # Check scenario name/description for risk keywords
            text = (
                (scenario.get("name", "") + " " + scenario.get("description", ""))
                .lower()
            )
            outcome = scenario.get("projected_outcome", {})

            # Try to infer risk level from scenario text
            if any(w in text for w in ("aggressiv", "hög risk", "high risk", "offensiv")):
                scenario_risk_levels.append(3)
            elif any(w in text for w in ("konservativ", "låg risk", "low risk", "försiktig")):
                scenario_risk_levels.append(1)
            elif any(w in text for w in ("balanserad", "moderate", "medel", "måttlig")):
                scenario_risk_levels.append(2)
            else:
                # Default to moderate if we can't determine
                scenario_risk_levels.append(2)

        if not scenario_risk_levels:
            return SuitabilityFactor(
                name="risk_profile_match",
                score=0.5,
                weight=FACTOR_WEIGHTS["risk_profile_match"],
                reason="Kan inte avgöra risknivå från scenarier.",
            )

        # Use the recommended scenario (first) or average
        recommended_risk = scenario_risk_levels[0]
        mismatch = abs(client_risk_level - recommended_risk)

        if mismatch == 0:
            score = 1.0
            reason = f"Rekommendation matchar klientens riskprofil ({risk_profile})."
        elif mismatch == 1:
            score = 0.7
            reason = f"Måttlig avvikelse från klientens riskprofil ({risk_profile})."
        else:
            score = 0.3
            reason = f"Stor avvikelse från klientens riskprofil ({risk_profile}). Motivering krävs."

        return SuitabilityFactor(
            name="risk_profile_match",
            score=score,
            weight=FACTOR_WEIGHTS["risk_profile_match"],
            reason=reason,
        )

    def _score_age_appropriateness(
        self, client: dict, recommendation_type: str
    ) -> SuitabilityFactor:
        """Score whether the recommendation type makes sense for the client's age.

        E.g., salary exchange with 2 years to retirement → low score.
        """
        age = self._client_age(client)
        retirement_age = client.get("desired_retirement_age")

        if age is None or retirement_age is None:
            return SuitabilityFactor(
                name="age_appropriateness",
                score=0.5,
                weight=FACTOR_WEIGHTS["age_appropriateness"],
                reason="Ålder eller önskad pensionsålder saknas — kan inte bedöma.",
            )

        years_to_retirement = retirement_age - age
        rt = recommendation_type.lower().strip()

        # Salary exchange: needs time to accumulate
        if rt == "salary_exchange":
            if years_to_retirement <= 2:
                score = 0.2
                reason = f"Bara {years_to_retirement} år till pension — löneväxling ger minimal effekt."
            elif years_to_retirement <= 5:
                score = 0.6
                reason = f"{years_to_retirement} år till pension — löneväxling ger begränsad men viss effekt."
            elif years_to_retirement <= 15:
                score = 1.0
                reason = f"{years_to_retirement} år till pension — god tidshorisont för löneväxling."
            else:
                score = 0.9
                reason = f"{years_to_retirement} år till pension — lång tidshorisont, bra för löneväxling."

        # Decumulation: should be near retirement
        elif rt in ("decumulation", "withdrawal_plan"):
            if years_to_retirement <= 0:
                score = 1.0
                reason = "Pensionerad eller vid pensionsålder — uttagsplanering är aktuellt."
            elif years_to_retirement <= 5:
                score = 0.8
                reason = f"{years_to_retirement} år till pension — bra tid att börja uttagsplanering."
            elif years_to_retirement <= 10:
                score = 0.5
                reason = f"{years_to_retirement} år till pension — tidigt för uttagsplanering men kan vara proaktivt."
            else:
                score = 0.2
                reason = f"{years_to_retirement} år till pension — för tidigt för uttagsplanering."

        # Transfer/allocation changes: better with longer horizon
        elif rt in ("transfer", "transfer_advice", "allocation_change"):
            if years_to_retirement <= 3:
                score = 0.5
                reason = f"Kort tid till pension ({years_to_retirement} år) — flytt/omplacering har begränsad tid att ge effekt."
            elif years_to_retirement <= 10:
                score = 0.8
                reason = f"{years_to_retirement} år till pension — rimlig tidshorisont."
            else:
                score = 1.0
                reason = f"{years_to_retirement} år till pension — lång tidshorisont ger utrymme."

        # Generic: moderate score for reasonable ages
        else:
            if 0 < years_to_retirement <= 40:
                score = 0.8
                reason = f"{years_to_retirement} år till pension — ingen åldersrelaterad invändning."
            elif years_to_retirement <= 0:
                score = 0.6
                reason = "Klienten har nått/passerat pensionsålder."
            else:
                score = 0.7
                reason = f"Ovanligt lång tid till pension ({years_to_retirement} år)."

        return SuitabilityFactor(
            name="age_appropriateness",
            score=score,
            weight=FACTOR_WEIGHTS["age_appropriateness"],
            reason=reason,
        )

    def _score_income_adequacy(
        self, client: dict, recommendation_type: str
    ) -> SuitabilityFactor:
        """Score whether the client's income supports the recommendation.

        Checks affordability for recommendation types involving costs/contributions.
        """
        income = self._parse_income(client)

        if income is None:
            return SuitabilityFactor(
                name="income_adequacy",
                score=0.5,
                weight=FACTOR_WEIGHTS["income_adequacy"],
                reason="Årsinkomst saknas — kan inte bedöma ekonomisk situation.",
            )

        rt = recommendation_type.lower().strip()

        if rt == "salary_exchange":
            if income >= 600_000:
                score = 1.0
                reason = f"Inkomst {income:,.0f} SEK — god marginal för löneväxling."
            elif income >= SALARY_EXCHANGE_MIN_INCOME:
                score = 0.7
                reason = f"Inkomst {income:,.0f} SEK — löneväxling möjlig men begränsad nytta."
            else:
                score = 0.2
                reason = f"Inkomst {income:,.0f} SEK — för låg för meningsfull löneväxling."
        else:
            # General income adequacy — higher income means more flexibility
            if income >= 500_000:
                score = 0.9
                reason = f"Inkomst {income:,.0f} SEK — god ekonomisk situation."
            elif income >= 300_000:
                score = 0.7
                reason = f"Inkomst {income:,.0f} SEK — rimlig ekonomisk situation."
            elif income >= 150_000:
                score = 0.5
                reason = f"Inkomst {income:,.0f} SEK — begränsad ekonomisk situation."
            else:
                score = 0.3
                reason = f"Inkomst {income:,.0f} SEK — svag ekonomisk situation, beakta kostnadskänslighet."

        return SuitabilityFactor(
            name="income_adequacy",
            score=score,
            weight=FACTOR_WEIGHTS["income_adequacy"],
            reason=reason,
        )

    def _score_agreement_eligibility(
        self, client: dict, recommendation_type: str
    ) -> SuitabilityFactor:
        """Score whether the collective agreement is compatible with the recommendation type."""
        agreement = client.get("collective_agreement")
        employment = client.get("employment_status")
        rt = recommendation_type.lower().strip()

        if not agreement or agreement in ("none", "other"):
            return SuitabilityFactor(
                name="agreement_eligibility",
                score=0.3,
                weight=FACTOR_WEIGHTS["agreement_eligibility"],
                reason=f"Kollektivavtal '{agreement or 'saknas'}' — behörighet oklart.",
            )

        if rt == "salary_exchange":
            if agreement in SALARY_EXCHANGE_AGREEMENTS and employment == "employed":
                score = 1.0
                reason = f"{agreement} + anställd — behörig för löneväxling."
            elif agreement in SALARY_EXCHANGE_AGREEMENTS:
                score = 0.5
                reason = f"{agreement} stödjer löneväxling men anställningsstatus är '{employment or 'okänd'}'."
            else:
                score = 0.0
                reason = f"{agreement} stödjer inte löneväxling."

        elif rt in ("transfer", "transfer_advice"):
            if agreement == "ITP2":
                score = 0.2
                reason = "ITP2 är förmånsbestämd — flytt av förmånsdelen ej möjlig."
            elif agreement in KNOWN_AGREEMENTS:
                score = 1.0
                reason = f"{agreement} — flytt av pensionskapital normalt möjlig."
            else:
                score = 0.3
                reason = f"Okänt avtal '{agreement}' — flyttbarhet oklart."

        elif rt in ("decumulation", "withdrawal_plan"):
            if agreement in KNOWN_AGREEMENTS:
                score = 0.8
                reason = f"{agreement} — uttagsalternativ finns men villkoren varierar."
            else:
                score = 0.3
                reason = f"Okänt avtal '{agreement}' — uttagsvillkor oklart."

        else:
            # Generic types: known agreement = eligible
            if agreement in KNOWN_AGREEMENTS:
                score = 1.0
                reason = f"{agreement} — inga kända behörighetshinder."
            else:
                score = 0.3
                reason = f"Okänt avtal '{agreement}' — behörighet oklart."

        return SuitabilityFactor(
            name="agreement_eligibility",
            score=score,
            weight=FACTOR_WEIGHTS["agreement_eligibility"],
            reason=reason,
        )

    def _score_data_completeness(self, client: dict) -> SuitabilityFactor:
        """Score based on how many client fields are filled.

        Each filled field adds proportionally to the score.
        """
        filled = 0
        total = len(COMPLETENESS_FIELDS)

        for field in COMPLETENESS_FIELDS:
            value = client.get(field)
            if value is not None and value != "" and value != "none":
                filled += 1

        score = filled / total if total > 0 else 0.0
        missing = [f for f in COMPLETENESS_FIELDS if not client.get(f) or client.get(f) == "none"]

        if not missing:
            reason = "Alla klientfält ifyllda."
        elif len(missing) <= 2:
            reason = f"Saknar: {', '.join(missing)}."
        else:
            reason = f"{filled}/{total} fält ifyllda. Saknar: {', '.join(missing)}."

        return SuitabilityFactor(
            name="data_completeness",
            score=round(score, 4),
            weight=FACTOR_WEIGHTS["data_completeness"],
            reason=reason,
        )

    def _compute_grade(self, total_score: float) -> str:
        """Map total score to a grade."""
        if total_score >= 0.7:
            return "high"
        elif total_score >= 0.4:
            return "moderate"
        else:
            return "low"

    def score(
        self,
        client: dict,
        recommendation_type: str,
        scenarios: list[dict] | None,
    ) -> SuitabilityResult:
        """Compute deterministic suitability score for a recommendation.

        Args:
            client: Dict with client fields from the API context builder.
                    Expected keys: name, date_of_birth, employment_status,
                    employer_name, collective_agreement, annual_income,
                    risk_profile, desired_retirement_age.
            recommendation_type: The recommendation type string (e.g. "salary_exchange").
            scenarios: List of scenario dicts from Pass 1 LLM output, or None.

        Returns:
            SuitabilityResult with total_score (0.0–1.0), factor breakdown, and grade.
        """
        factors = [
            self._score_risk_profile_match(client, scenarios),
            self._score_age_appropriateness(client, recommendation_type),
            self._score_income_adequacy(client, recommendation_type),
            self._score_agreement_eligibility(client, recommendation_type),
            self._score_data_completeness(client),
        ]

        total = sum(f.score * f.weight for f in factors)
        total = round(min(max(total, 0.0), 1.0), 4)

        return SuitabilityResult(
            total_score=total,
            factors=factors,
            grade=self._compute_grade(total),
        )
