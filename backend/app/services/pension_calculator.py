"""Deterministic Swedish pension calculator.

All numbers are traceable to published sources (Pensionsmyndigheten, Collectum,
Fora, SKR, SPV). IBB and tax breakpoints are in config dicts at the top so
they're easy to update yearly.

Key sources:
- IBB: Pensionsmyndigheten (https://www.pensionsmyndigheten.se)
- ITP1/ITP2 rates: Collectum
- SAF-LO rates: Fora
- KAP-KL/AKAP-KL rates: SKR (Sveriges Kommuner och Regioner)
- PA16 rates: SPV (Statens tjänstepensionsverk)
- Tax breakpoints: Skatteverket
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Yearly configuration — update these when new figures are published
# ---------------------------------------------------------------------------

IBB_BY_YEAR: dict[int, int] = {
    2024: 76_200,
    2025: 80_600,
    2026: 83_600,
}

# State income tax breakpoint (skiktgräns) for additional 20% state tax
TAX_BREAKPOINTS: dict[int, int] = {
    2024: 598_500,
    2025: 615_700,
    2026: 613_900,
}

# Average municipal tax rate in Sweden
MUNICIPAL_TAX_RATE: float = 0.32

# State income tax rate above breakpoint
STATE_TAX_RATE: float = 0.20

# Allmän pension rates (source: Pensionsmyndigheten)
ALLMAN_INKOMSTPENSION_RATE: float = 0.16
ALLMAN_PREMIEPENSION_RATE: float = 0.025
PGI_FACTOR: float = 0.93  # PGI ≈ income × 0.93 (after grundavdrag approximation)
ALLMAN_CEILING_FACTOR: float = 8.07  # PGI ceiling = 8.07 × IBB

# Tjänstepension ceiling factor (7.5 × IBB is the threshold for higher rate)
TJANSTE_CEILING_FACTOR: float = 7.5

# Tjänstepension contribution rates by agreement
# Format: {"below_ceiling": rate, "above_ceiling": rate, "type": "dc"|"db"|"mixed"}
TJANSTE_RATES: dict[str, dict[str, Any]] = {
    "ITP1": {
        "below_ceiling": 0.045,
        "above_ceiling": 0.30,
        "type": "dc",
        "source": "Collectum — ITP1 premiebestämd",
    },
    "ITP2": {
        "type": "db",
        "source": "Collectum — ITP2 förmånsbestämd (ej premiebaserad beräkning)",
    },
    "SAF_LO": {
        "below_ceiling": 0.045,
        "above_ceiling": 0.30,
        "type": "dc",
        "source": "Fora — Avtalspension SAF-LO",
    },
    "KAP_KL": {
        "below_ceiling": 0.045,
        "above_ceiling": 0.30,
        "type": "dc",
        "source": "SKR — KAP-KL premiebestämd del",
    },
    "AKAP_KL": {
        "below_ceiling": 0.045,
        "above_ceiling": 0.30,
        "type": "dc",
        "age_supplement": True,
        "source": "SKR — AKAP-KL (4.5% + ålderstillägg 0–2%)",
    },
    "PA16": {
        "below_ceiling": 0.045,
        "above_ceiling": 0.30,
        "type": "mixed",
        "source": "SPV — PA16 avdelning 1 (premiebestämd), avdelning 2 (förmånsbestämd)",
    },
}

# Social fee savings factor for salary exchange
# Employer saves ~31.42% social fees on exchanged amount, passes ~6% to employee
SALARY_EXCHANGE_EMPLOYER_FACTOR: float = 1.06

# Default salary exchange amount as fraction of income above ceiling
DEFAULT_EXCHANGE_FRACTION: float = 0.05  # 5% of salary as default exchange


# ---------------------------------------------------------------------------
# Pydantic output models
# ---------------------------------------------------------------------------


class PensionEstimate(BaseModel):
    """Deterministic pension contribution estimate for a client."""

    ibb: int = Field(description="Current year inkomstbasbelopp (SEK)")
    yearly_contribution: dict[str, int | None] = Field(
        description="Breakdown by pillar: allman, tjanste, privat (SEK/year)"
    )
    contribution_rates: dict[str, Any] = Field(
        description="The rates and formulas used, for transparency and verification"
    )
    projected_monthly_pension: int | None = Field(
        default=None,
        description="Rough projected monthly pension (SEK), if enough data",
    )
    salary_exchange_potential: dict[str, Any] | None = Field(
        default=None,
        description="Tax savings estimate for salary exchange, if applicable",
    )
    notes: list[str] = Field(
        default_factory=list,
        description="Caveats, limitations, and data gaps",
    )


# ---------------------------------------------------------------------------
# Calculator
# ---------------------------------------------------------------------------


class PensionCalculator:
    """Deterministic Swedish pension math.

    All numbers are verifiable against published sources. The calculator
    handles missing data gracefully — if a field is None, it skips the
    dependent calculation and adds a note.
    """

    def _current_year(self) -> int:
        return date.today().year

    def _get_ibb(self, year: int | None = None) -> int:
        """Get IBB for the given year, falling back to the latest available."""
        y = year or self._current_year()
        if y in IBB_BY_YEAR:
            return IBB_BY_YEAR[y]
        # Fall back to latest known
        latest = max(IBB_BY_YEAR.keys())
        return IBB_BY_YEAR[latest]

    def _get_tax_breakpoint(self, year: int | None = None) -> int:
        y = year or self._current_year()
        if y in TAX_BREAKPOINTS:
            return TAX_BREAKPOINTS[y]
        latest = max(TAX_BREAKPOINTS.keys())
        return TAX_BREAKPOINTS[latest]

    def _parse_income(self, client: dict) -> float | None:
        """Safely parse annual_income from client dict (may be str, int, float, or None)."""
        raw = client.get("annual_income")
        if raw is None:
            return None
        try:
            return float(raw)
        except (ValueError, TypeError):
            return None

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

    def _calc_allman(self, income: float, ibb: int) -> dict[str, Any]:
        """Calculate allmän pension contributions.

        Source: Pensionsmyndigheten
        - Inkomstpension: 16% of PGI up to 8.07 × IBB
        - Premiepension: 2.5% of PGI up to 8.07 × IBB
        - PGI ≈ income × 0.93
        """
        pgi = income * PGI_FACTOR
        pgi_ceiling = ALLMAN_CEILING_FACTOR * ibb
        capped_pgi = min(pgi, pgi_ceiling)

        inkomstpension = capped_pgi * ALLMAN_INKOMSTPENSION_RATE
        premiepension = capped_pgi * ALLMAN_PREMIEPENSION_RATE

        return {
            "inkomstpension": round(inkomstpension),
            "premiepension": round(premiepension),
            "total": round(inkomstpension + premiepension),
            "pgi": round(capped_pgi),
            "pgi_ceiling": round(pgi_ceiling),
            "pgi_capped": pgi > pgi_ceiling,
        }

    def _calc_tjanste(
        self, income: float, agreement: str, ibb: int, age: int | None
    ) -> dict[str, Any] | None:
        """Calculate tjänstepension contribution by collective agreement.

        Returns contribution amount and the rates used, or None for unknown agreements.
        """
        rates = TJANSTE_RATES.get(agreement)
        if rates is None:
            return None

        if rates["type"] == "db":
            # Defined benefit — cannot compute contribution directly
            return {
                "type": "defined_benefit",
                "contribution": None,
                "source": rates["source"],
                "note": "Förmånsbestämd — premien beräknas av försäkringsgivaren, ej av arbetsgivarens lönekostnad",
            }

        ceiling = TJANSTE_CEILING_FACTOR * ibb
        below_rate = rates["below_ceiling"]
        above_rate = rates["above_ceiling"]

        if income <= ceiling:
            contribution = income * below_rate
            breakdown = {"below_ceiling": round(contribution), "above_ceiling": 0}
        else:
            below_part = ceiling * below_rate
            above_part = (income - ceiling) * above_rate
            contribution = below_part + above_part
            breakdown = {
                "below_ceiling": round(below_part),
                "above_ceiling": round(above_part),
            }

        # AKAP-KL age supplement: +0.5% at 25, +1% at 30, +1.5% at 35, +2% at 40+
        age_supplement = 0
        if rates.get("age_supplement") and age is not None:
            if age >= 40:
                age_supplement = income * 0.02
            elif age >= 35:
                age_supplement = income * 0.015
            elif age >= 30:
                age_supplement = income * 0.01
            elif age >= 25:
                age_supplement = income * 0.005
            breakdown["age_supplement"] = round(age_supplement)

        total = contribution + age_supplement

        result: dict[str, Any] = {
            "type": rates["type"],
            "contribution": round(total),
            "breakdown": breakdown,
            "ceiling": round(ceiling),
            "rates": {"below_ceiling": below_rate, "above_ceiling": above_rate},
            "source": rates["source"],
        }

        if rates["type"] == "mixed":
            result["note"] = "PA16 har både premiebestämd (avd 1) och förmånsbestämd (avd 2) del. Beräkningen visar avd 1."

        return result

    def _calc_salary_exchange(
        self, income: float, ibb: int
    ) -> dict[str, Any] | None:
        """Estimate salary exchange tax benefit.

        Only meaningful if income is above the ceiling (7.5 × IBB), where the
        employer pension contribution jumps from 4.5% to 30%.

        Source: General Swedish salary exchange practice.
        """
        ceiling = TJANSTE_CEILING_FACTOR * ibb
        breakpoint = self._get_tax_breakpoint()

        # Suggest exchange amount: 5% of salary, capped at a reasonable amount
        exchange_amount = round(income * DEFAULT_EXCHANGE_FRACTION)

        # Calculate marginal tax rate
        if income > breakpoint:
            marginal_tax = MUNICIPAL_TAX_RATE + STATE_TAX_RATE
        else:
            marginal_tax = MUNICIPAL_TAX_RATE

        # What the employee gives up (net of tax)
        lost_net_income = exchange_amount * (1 - marginal_tax)

        # What the employer contributes to pension (with social fee savings pass-through)
        employer_pension_contribution = exchange_amount * SALARY_EXCHANGE_EMPLOYER_FACTOR

        net_benefit = employer_pension_contribution - lost_net_income

        return {
            "exchange_amount_sek": exchange_amount,
            "marginal_tax_rate": round(marginal_tax, 4),
            "tax_breakpoint": breakpoint,
            "income_above_breakpoint": income > breakpoint,
            "lost_net_income": round(lost_net_income),
            "employer_pension_contribution": round(employer_pension_contribution),
            "net_benefit_sek": round(net_benefit),
            "income_above_ceiling": income > ceiling,
            "note": (
                "Löneväxling är mest fördelaktig vid inkomst över taket (7.5 × IBB) "
                "där arbetsgivaren sparar sociala avgifter. Beräkningen är en förenklad uppskattning."
            ),
        }

    def calculate(self, client: dict) -> PensionEstimate:
        """Calculate pension contributions for a client.

        Args:
            client: Dict with client fields as returned by the API context builder.
                    Expected keys: annual_income, collective_agreement, date_of_birth,
                    employment_status, desired_retirement_age, etc.

        Returns:
            PensionEstimate with all computed values and source references.
        """
        year = self._current_year()
        ibb = self._get_ibb(year)
        income = self._parse_income(client)
        agreement = client.get("collective_agreement")
        age = self._client_age(client)
        notes: list[str] = []

        contribution_rates: dict[str, Any] = {
            "year": year,
            "ibb": ibb,
            "allman_pension": {
                "inkomstpension": ALLMAN_INKOMSTPENSION_RATE,
                "premiepension": ALLMAN_PREMIEPENSION_RATE,
                "pgi_factor": PGI_FACTOR,
                "ceiling_factor": ALLMAN_CEILING_FACTOR,
            },
        }

        yearly_contribution: dict[str, int | None] = {
            "allman": None,
            "tjanste": None,
            "privat": None,  # Private savings — cannot be computed, always None
        }

        # --- Allmän pension ---
        if income is not None:
            allman = self._calc_allman(income, ibb)
            yearly_contribution["allman"] = allman["total"]
            contribution_rates["allman_details"] = allman
            if allman["pgi_capped"]:
                notes.append(
                    f"Inkomsten överstiger PGI-taket ({allman['pgi_ceiling']:,} SEK). "
                    "Allmän pension beräknas på taket."
                )
        else:
            notes.append("Årsinkomst saknas — allmän pension kan ej beräknas.")

        # --- Tjänstepension ---
        if income is not None and agreement:
            tjanste = self._calc_tjanste(income, agreement, ibb, age)
            if tjanste is not None:
                yearly_contribution["tjanste"] = tjanste.get("contribution")
                contribution_rates["tjanste_details"] = tjanste
                if tjanste.get("note"):
                    notes.append(tjanste["note"])
            else:
                notes.append(
                    f"Kollektivavtal '{agreement}' har inga konfigurerade bidragssatser."
                )
        elif income is None:
            notes.append("Årsinkomst saknas — tjänstepension kan ej beräknas.")
        elif not agreement:
            notes.append("Kollektivavtal saknas — tjänstepension kan ej beräknas.")

        # --- Privat ---
        notes.append("Privat pensionssparande kan ej beräknas — uppgift saknas.")

        # --- Projected monthly pension (rough estimate) ---
        projected_monthly: int | None = None
        retirement_age = client.get("desired_retirement_age")
        if income is not None and age is not None and retirement_age is not None:
            years_to_retirement = max(retirement_age - age, 0)
            if years_to_retirement > 0:
                # Very rough: sum yearly contributions × years, assume 3% real return,
                # then divide by 240 months (20 year payout)
                total_yearly = sum(v for v in yearly_contribution.values() if v is not None)
                if total_yearly > 0:
                    # Future value of annuity: PMT × ((1+r)^n - 1) / r
                    r = 0.03  # 3% real annual return assumption
                    fv = total_yearly * (((1 + r) ** years_to_retirement - 1) / r)
                    payout_months = 20 * 12  # 20 year payout period
                    projected_monthly = round(fv / payout_months)
                    notes.append(
                        f"Uppskattad månadspension baseras på {years_to_retirement} år till pension, "
                        "3% real avkastning, 20 års utbetalningsperiod. Mycket förenklad beräkning."
                    )

        # --- Salary exchange potential ---
        salary_exchange: dict[str, Any] | None = None
        if income is not None:
            salary_exchange = self._calc_salary_exchange(income, ibb)

        return PensionEstimate(
            ibb=ibb,
            yearly_contribution=yearly_contribution,
            contribution_rates=contribution_rates,
            projected_monthly_pension=projected_monthly,
            salary_exchange_potential=salary_exchange,
            notes=notes,
        )
