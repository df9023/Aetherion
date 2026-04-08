"""Eligibility checker for Swedish pension recommendations.

Uses lookup tables for agreement-provider mappings and recommendation type
eligibility rules. All data is from published sources (Collectum, Fora, SKR, SPV).

Sources:
- ITP1 providers: Collectum valcentral (collectum.se)
- SAF-LO providers: Fora valcentral (fora.se)
- KAP-KL/AKAP-KL: SKR (skr.se)
- PA16: SPV (spv.se)
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Agreement → provider lookup tables
# ---------------------------------------------------------------------------

AGREEMENT_PROVIDERS: dict[str, dict[str, Any]] = {
    "ITP1": {
        "valcentral": "Collectum",
        "default_provider": "Alecta",
        "providers": [
            "Alecta", "AMF", "Folksam", "Skandia", "SPP",
            "Länsförsäkringar", "SEB", "Nordea", "Handelsbanken",
        ],
        "source": "Collectum — ITP1 premiebestämd",
    },
    "ITP2": {
        "valcentral": "Collectum",
        "default_provider": "Alecta",
        "providers": ["Alecta"],
        "source": "Collectum — ITP2 förmånsbestämd (Alecta obligatorisk för förmånsdelen)",
        "note": "ITPK-delen (premiebestämd tillägg) kan placeras hos fler leverantörer",
    },
    "SAF_LO": {
        "valcentral": "Fora",
        "default_provider": "AMF",
        "providers": [
            "AMF", "Folksam", "Handelsbanken", "Länsförsäkringar",
            "Nordea", "SEB", "Skandia", "Swedbank",
        ],
        "source": "Fora — Avtalspension SAF-LO",
    },
    "KAP_KL": {
        "valcentral": None,
        "default_provider": None,
        "providers": [],
        "source": "SKR — KAP-KL (arbetsgivarens val av leverantör)",
        "note": "Leverantörsval styrs av arbetsgivaren, ej individuellt val",
    },
    "AKAP_KL": {
        "valcentral": None,
        "default_provider": None,
        "providers": [],
        "source": "SKR — AKAP-KL (arbetsgivarens val av leverantör)",
        "note": "Leverantörsval styrs av arbetsgivaren, ej individuellt val",
    },
    "PA16": {
        "valcentral": "SPV",
        "default_provider": "Kåpan",
        "providers": ["Kåpan"],
        "source": "SPV — PA16 statlig tjänstepension",
        "note": "Avdelning 1 (premiebestämd) kan placeras via SPV:s fondtorg",
    },
}

# Agreements eligible for salary exchange
SALARY_EXCHANGE_AGREEMENTS: set[str] = {"ITP1", "ITP2", "SAF_LO", "KAP_KL", "AKAP_KL"}

# Minimum income threshold for salary exchange to be meaningful (SEK)
SALARY_EXCHANGE_MIN_INCOME: int = 300_000

# Agreements where transfer advice applies (most DC agreements)
TRANSFER_ELIGIBLE_AGREEMENTS: set[str] = {"ITP1", "SAF_LO", "KAP_KL", "AKAP_KL", "PA16"}


# ---------------------------------------------------------------------------
# Pydantic output model
# ---------------------------------------------------------------------------


class EligibilityResult(BaseModel):
    """Result of an eligibility check for a given recommendation type."""

    eligible: bool = Field(description="Whether the client is eligible for this recommendation type")
    reasons: list[str] = Field(
        default_factory=list,
        description="Reasons why the client is or is not eligible",
    )
    eligible_providers: list[str] = Field(
        default_factory=list,
        description="Providers relevant for this agreement",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Things to be aware of even if eligible",
    )


# ---------------------------------------------------------------------------
# Checker
# ---------------------------------------------------------------------------


class EligibilityChecker:
    """Check eligibility for recommendation types based on client situation.

    Uses lookup tables for agreement-provider mappings and rule-based checks
    for recommendation type compatibility.
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

    def _get_providers(self, agreement: str) -> list[str]:
        """Get eligible providers for a collective agreement."""
        info = AGREEMENT_PROVIDERS.get(agreement)
        if info is None:
            return []
        return info["providers"]

    def _check_salary_exchange(self, client: dict) -> EligibilityResult:
        """Salary exchange: requires employed + eligible agreement + sufficient income."""
        agreement = client.get("collective_agreement")
        employment = client.get("employment_status")
        income = self._parse_income(client)
        age = self._client_age(client)
        retirement_age = client.get("desired_retirement_age")

        reasons: list[str] = []
        warnings: list[str] = []
        eligible = True

        # Employment check
        if employment != "employed":
            eligible = False
            reasons.append(
                f"Löneväxling kräver anställning. Nuvarande status: {employment or 'okänd'}."
            )
        else:
            reasons.append("Anställd — grundkrav uppfyllt.")

        # Agreement check
        if agreement not in SALARY_EXCHANGE_AGREEMENTS:
            eligible = False
            reasons.append(
                f"Kollektivavtal '{agreement or 'saknas'}' stödjer inte löneväxling."
            )
        else:
            reasons.append(f"Kollektivavtal {agreement} stödjer löneväxling.")

        # Income check
        if income is not None:
            if income < SALARY_EXCHANGE_MIN_INCOME:
                eligible = False
                reasons.append(
                    f"Årsinkomst {income:,.0f} SEK är under miniminivå "
                    f"({SALARY_EXCHANGE_MIN_INCOME:,} SEK) för löneväxling."
                )
            else:
                reasons.append(f"Årsinkomst {income:,.0f} SEK är tillräcklig.")
        else:
            warnings.append("Årsinkomst saknas — kan inte bekräfta att löneväxling är ekonomiskt fördelaktig.")

        # Age/retirement proximity warning
        if age is not None and retirement_age is not None:
            years_left = retirement_age - age
            if years_left <= 2:
                warnings.append(
                    f"Kort tid till pension ({years_left} år). Löneväxling ger begränsad effekt."
                )
            elif years_left <= 5:
                warnings.append(
                    f"{years_left} år till pension. Löneväxling ger effekt men tidshorisont är kort."
                )

        providers = self._get_providers(agreement) if agreement else []
        return EligibilityResult(
            eligible=eligible,
            reasons=reasons,
            eligible_providers=providers,
            warnings=warnings,
        )

    def _check_transfer_advice(self, client: dict) -> EligibilityResult:
        """Transfer advice: applicable to most DC agreements, check lock-in."""
        agreement = client.get("collective_agreement")
        reasons: list[str] = []
        warnings: list[str] = []

        if agreement in TRANSFER_ELIGIBLE_AGREEMENTS:
            eligible = True
            reasons.append(f"Kollektivavtal {agreement} tillåter flytt av pensionskapital.")
        elif agreement == "ITP2":
            eligible = False
            reasons.append("ITP2 är förmånsbestämd — kapitalflytt är inte möjlig för förmånsdelen.")
            warnings.append("ITPK-delen (premiebestämd) kan eventuellt flyttas separat.")
        elif agreement:
            eligible = True
            reasons.append(f"Kollektivavtal {agreement} — flyttbarhet behöver verifieras.")
            warnings.append("Kontrollera villkor och eventuella flyttavgifter hos nuvarande leverantör.")
        else:
            eligible = False
            reasons.append("Kollektivavtal saknas — kan inte bedöma flyttbarhet.")

        warnings.append("Kontrollera alltid eventuella efterköps-/flyttavgifter och uppsägningstider.")

        providers = self._get_providers(agreement) if agreement else []
        return EligibilityResult(
            eligible=eligible,
            reasons=reasons,
            eligible_providers=providers,
            warnings=warnings,
        )

    def _check_survivor_protection(self, client: dict) -> EligibilityResult:
        """Survivor protection: always relevant, options differ by agreement."""
        agreement = client.get("collective_agreement")
        reasons: list[str] = ["Efterlevandeskydd är relevant för alla — alternativen varierar."]
        warnings: list[str] = []

        if agreement in ("ITP1", "ITP2"):
            warnings.append(
                "ITP inkluderar familjeskydd via Alecta. Kontrollera om tilläggsval behövs."
            )
        elif agreement in ("SAF_LO",):
            warnings.append(
                "SAF-LO inkluderar TGL (tjänstegrupplivförsäkring). Kontrollera om tilläggsval behövs."
            )
        elif agreement in ("KAP_KL", "AKAP_KL"):
            warnings.append(
                "Kommunal tjänstepension inkluderar efterlevandepension. Kontrollera om det täcker behovet."
            )
        elif agreement == "PA16":
            warnings.append(
                "PA16 inkluderar efterlevandeskydd via SPV. Kontrollera nivå."
            )

        providers = self._get_providers(agreement) if agreement else []
        return EligibilityResult(
            eligible=True,
            reasons=reasons,
            eligible_providers=providers,
            warnings=warnings,
        )

    def _check_decumulation(self, client: dict) -> EligibilityResult:
        """Decumulation: only for retired or near-retirement clients."""
        employment = client.get("employment_status")
        age = self._client_age(client)
        retirement_age = client.get("desired_retirement_age")
        agreement = client.get("collective_agreement")

        reasons: list[str] = []
        warnings: list[str] = []
        eligible = False

        if employment == "retired":
            eligible = True
            reasons.append("Klienten är pensionerad — uttagsplanering är aktuellt.")
        elif age is not None and retirement_age is not None:
            years_left = retirement_age - age
            if years_left <= 5:
                eligible = True
                reasons.append(
                    f"{years_left} år till pension — uttagsplanering bör påbörjas."
                )
            else:
                reasons.append(
                    f"{years_left} år till pension — för tidigt för uttagsplanering. "
                    "Rekommenderas normalt inom 5 år före pension."
                )
        elif age is not None and age >= 60:
            eligible = True
            reasons.append(f"Ålder {age} — uttagsplanering kan vara aktuellt.")
            warnings.append("Önskad pensionsålder saknas — fråga klienten.")
        else:
            reasons.append("Klienten verkar inte vara nära pensionsåldern.")
            warnings.append("Kontrollera klientens pensionsplaner.")

        if eligible:
            warnings.append(
                "Uttagsordning (vilken pension som tas ut först) har stor skatteeffekt — "
                "rekommendera individuell analys."
            )

        providers = self._get_providers(agreement) if agreement else []
        return EligibilityResult(
            eligible=eligible,
            reasons=reasons,
            eligible_providers=providers,
            warnings=warnings,
        )

    def _check_generic(self, client: dict, recommendation_type: str) -> EligibilityResult:
        """Generic check for recommendation types without specific rules."""
        agreement = client.get("collective_agreement")
        providers = self._get_providers(agreement) if agreement else []

        return EligibilityResult(
            eligible=True,
            reasons=[f"Ingen specifik behörighetsbegränsning för '{recommendation_type}'."],
            eligible_providers=providers,
            warnings=["Verifiera behörighet manuellt mot avtalsvillkor."],
        )

    def check(self, client: dict, recommendation_type: str) -> EligibilityResult:
        """Check eligibility for a recommendation type given a client's situation.

        Args:
            client: Dict with client fields (employment_status, collective_agreement,
                    annual_income, date_of_birth, desired_retirement_age, etc.)
            recommendation_type: The type of recommendation (matches RecommendationType
                    or CaseType values).

        Returns:
            EligibilityResult with eligibility status, reasons, providers, and warnings.
        """
        # Normalize the recommendation type to handle both enum values and raw strings
        rt = recommendation_type.lower().strip()

        if rt == "salary_exchange":
            return self._check_salary_exchange(client)
        elif rt in ("transfer", "transfer_advice"):
            return self._check_transfer_advice(client)
        elif rt in ("survivor_protection", "coverage_change"):
            return self._check_survivor_protection(client)
        elif rt in ("decumulation", "withdrawal_plan"):
            return self._check_decumulation(client)
        else:
            # pension_review, product_selection, allocation_change, retirement_planning, other
            return self._check_generic(client, rt)
