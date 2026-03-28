"""Tests for the deterministic pension calculator.

All expected values are hand-verified against published rates:
- IBB 2026: 83,600 SEK
- Tjänstepension ceiling: 7.5 × IBB = 627,000 SEK
- PGI ceiling: 8.07 × IBB = 674,652 SEK
- ITP1/SAF-LO: 4.5% below ceiling, 30% above
- Allmän: 16% inkomstpension + 2.5% premiepension on PGI (income × 0.93)
"""

import pytest
from unittest.mock import patch

from app.services.pension_calculator import (
    PensionCalculator,
    PensionEstimate,
    IBB_BY_YEAR,
    TAX_BREAKPOINTS,
    TJANSTE_CEILING_FACTOR,
    ALLMAN_CEILING_FACTOR,
)


@pytest.fixture
def calc() -> PensionCalculator:
    return PensionCalculator()


# ---------------------------------------------------------------------------
# IBB lookup
# ---------------------------------------------------------------------------


class TestIBBLookup:
    def test_ibb_2024(self, calc: PensionCalculator):
        """IBB for 2024 should be 76,200 SEK (Pensionsmyndigheten)."""
        assert calc._get_ibb(2024) == 76_200

    def test_ibb_2025(self, calc: PensionCalculator):
        """IBB for 2025 should be 80,600 SEK."""
        assert calc._get_ibb(2025) == 80_600

    def test_ibb_2026(self, calc: PensionCalculator):
        """IBB for 2026 should be 83,600 SEK."""
        assert calc._get_ibb(2026) == 83_600

    def test_ibb_unknown_year_falls_back_to_latest(self, calc: PensionCalculator):
        """A future year not in config should fall back to the latest known IBB."""
        latest_year = max(IBB_BY_YEAR.keys())
        assert calc._get_ibb(2099) == IBB_BY_YEAR[latest_year]


# ---------------------------------------------------------------------------
# ITP1 — defined contribution
# ---------------------------------------------------------------------------


class TestITP1:
    """ITP1: 4.5% on salary <= 7.5 × IBB, 30% above."""

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_itp1_below_ceiling_contribution_rate(self, _mock, calc: PensionCalculator):
        """650k income is above 627k ceiling → split contribution.
        Below ceiling: 627,000 × 4.5% = 28,215
        Above ceiling: 23,000 × 30% = 6,900
        Total: 35,115
        """
        client = {
            "annual_income": "650000",
            "collective_agreement": "ITP1",
            "date_of_birth": "1980-05-15",
        }
        est = calc.calculate(client)
        assert est.yearly_contribution["tjanste"] == 35_115

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_itp1_below_ceiling_breakdown(self, _mock, calc: PensionCalculator):
        """Verify the breakdown dict for a split contribution."""
        client = {
            "annual_income": "650000",
            "collective_agreement": "ITP1",
            "date_of_birth": "1980-05-15",
        }
        est = calc.calculate(client)
        details = est.contribution_rates["tjanste_details"]
        assert details["breakdown"]["below_ceiling"] == 28_215
        assert details["breakdown"]["above_ceiling"] == 6_900

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_itp1_entirely_below_ceiling(self, _mock, calc: PensionCalculator):
        """400k < 627k ceiling → all at 4.5%, nothing above.
        400,000 × 4.5% = 18,000
        """
        client = {
            "annual_income": "400000",
            "collective_agreement": "ITP1",
            "date_of_birth": "1990-01-01",
        }
        est = calc.calculate(client)
        assert est.yearly_contribution["tjanste"] == 18_000
        details = est.contribution_rates["tjanste_details"]
        assert details["breakdown"]["above_ceiling"] == 0

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_itp1_income_exactly_at_ceiling(self, _mock, calc: PensionCalculator):
        """Income exactly at 627,000 → all at 4.5%, zero above.
        627,000 × 4.5% = 28,215
        """
        client = {
            "annual_income": "627000",
            "collective_agreement": "ITP1",
            "date_of_birth": "1985-06-15",
        }
        est = calc.calculate(client)
        assert est.yearly_contribution["tjanste"] == 28_215
        details = est.contribution_rates["tjanste_details"]
        assert details["breakdown"]["above_ceiling"] == 0


# ---------------------------------------------------------------------------
# High earner
# ---------------------------------------------------------------------------


class TestHighEarner:
    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_high_earner_itp1_split(self, _mock, calc: PensionCalculator):
        """1.2M income, ITP1:
        Below ceiling: 627,000 × 4.5% = 28,215
        Above ceiling: 573,000 × 30% = 171,900
        Total: 200,115
        """
        client = {
            "annual_income": "1200000",
            "collective_agreement": "ITP1",
            "date_of_birth": "1975-03-20",
        }
        est = calc.calculate(client)
        assert est.yearly_contribution["tjanste"] == 200_115

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_high_earner_allman_pension_capped(self, _mock, calc: PensionCalculator):
        """1.2M income → PGI = 1,116,000, capped at 674,652.
        Inkomstpension: 674,652 × 16% = 107,944.32
        Premiepension: 674,652 × 2.5% = 16,866.3
        Total (rounded from sum): round(124,810.62) = 124,811
        Note: total is round(sum), not sum(rounds), so may differ by 1.
        """
        client = {
            "annual_income": "1200000",
            "collective_agreement": "ITP1",
            "date_of_birth": "1975-03-20",
        }
        est = calc.calculate(client)
        details = est.contribution_rates["allman_details"]
        assert details["pgi_capped"] is True
        assert details["inkomstpension"] == round(674_652 * 0.16)
        assert details["premiepension"] == round(674_652 * 0.025)
        # Total is round(raw_inkomst + raw_premie), may differ from sum of individually rounded parts by ±1
        expected_total = round(674_652 * 0.16 + 674_652 * 0.025)
        assert est.yearly_contribution["allman"] == expected_total


# ---------------------------------------------------------------------------
# SAF-LO
# ---------------------------------------------------------------------------


class TestSAFLO:
    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_saf_lo_below_ceiling(self, _mock, calc: PensionCalculator):
        """SAF-LO at 400k: same rates as ITP1 for DC part.
        400,000 × 4.5% = 18,000
        """
        client = {
            "annual_income": "400000",
            "collective_agreement": "SAF_LO",
            "date_of_birth": "1990-01-01",
        }
        est = calc.calculate(client)
        assert est.yearly_contribution["tjanste"] == 18_000

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_saf_lo_source_reference(self, _mock, calc: PensionCalculator):
        """SAF-LO contribution rates should reference Fora."""
        client = {
            "annual_income": "400000",
            "collective_agreement": "SAF_LO",
            "date_of_birth": "1990-01-01",
        }
        est = calc.calculate(client)
        assert "Fora" in est.contribution_rates["tjanste_details"]["source"]


# ---------------------------------------------------------------------------
# ITP2 — defined benefit
# ---------------------------------------------------------------------------


class TestITP2:
    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_itp2_defined_benefit_no_contribution(self, _mock, calc: PensionCalculator):
        """ITP2 is defined benefit → contribution should be None."""
        client = {
            "annual_income": "600000",
            "collective_agreement": "ITP2",
            "date_of_birth": "1970-01-01",
        }
        est = calc.calculate(client)
        assert est.yearly_contribution["tjanste"] is None

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_itp2_type_is_defined_benefit(self, _mock, calc: PensionCalculator):
        """ITP2 tjanste_details should indicate defined_benefit type."""
        client = {
            "annual_income": "600000",
            "collective_agreement": "ITP2",
            "date_of_birth": "1970-01-01",
        }
        est = calc.calculate(client)
        details = est.contribution_rates["tjanste_details"]
        assert details["type"] == "defined_benefit"


# ---------------------------------------------------------------------------
# Allmän pension
# ---------------------------------------------------------------------------


class TestAllmanPension:
    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_allman_pension_below_pgi_ceiling(self, _mock, calc: PensionCalculator):
        """650k: PGI = 604,500 < ceiling 674,652 → not capped.
        Inkomstpension: 604,500 × 16% = 96,720
        Premiepension: 604,500 × 2.5% = 15,112 (rounded)
        """
        client = {
            "annual_income": "650000",
            "collective_agreement": "ITP1",
            "date_of_birth": "1980-05-15",
        }
        est = calc.calculate(client)
        details = est.contribution_rates["allman_details"]
        assert details["pgi_capped"] is False
        assert details["pgi"] == round(650_000 * 0.93)
        assert details["inkomstpension"] == round(604_500 * 0.16)
        assert details["premiepension"] == round(604_500 * 0.025)

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_allman_pension_pgi_ceiling_value(self, _mock, calc: PensionCalculator):
        """PGI ceiling should be 8.07 × 83,600 = 674,652."""
        client = {
            "annual_income": "650000",
            "collective_agreement": "ITP1",
            "date_of_birth": "1980-05-15",
        }
        est = calc.calculate(client)
        details = est.contribution_rates["allman_details"]
        assert details["pgi_ceiling"] == round(ALLMAN_CEILING_FACTOR * 83_600)


# ---------------------------------------------------------------------------
# AKAP-KL age supplement
# ---------------------------------------------------------------------------


class TestAKAPKL:
    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_akap_kl_age_supplement_over_40(self, _mock, calc: PensionCalculator):
        """AKAP-KL client age 45: base 4.5% + 2% age supplement.
        Base at 500k (below ceiling): 500,000 × 4.5% = 22,500
        Age supplement: 500,000 × 2% = 10,000
        Total: 32,500
        """
        client = {
            "annual_income": "500000",
            "collective_agreement": "AKAP_KL",
            "date_of_birth": "1981-01-01",  # ~45 in 2026
        }
        est = calc.calculate(client)
        assert est.yearly_contribution["tjanste"] == 32_500

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_akap_kl_age_supplement_under_25(self, _mock, calc: PensionCalculator):
        """AKAP-KL client age 22: no age supplement.
        Base at 400k: 400,000 × 4.5% = 18,000
        """
        client = {
            "annual_income": "400000",
            "collective_agreement": "AKAP_KL",
            "date_of_birth": "2004-01-01",  # ~22 in 2026
        }
        est = calc.calculate(client)
        assert est.yearly_contribution["tjanste"] == 18_000

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_akap_kl_age_supplement_30(self, _mock, calc: PensionCalculator):
        """AKAP-KL client age 30: +1% supplement.
        Base at 400k: 400,000 × 4.5% = 18,000
        Supplement: 400,000 × 1% = 4,000
        Total: 22,000
        """
        client = {
            "annual_income": "400000",
            "collective_agreement": "AKAP_KL",
            "date_of_birth": "1996-01-01",  # ~30 in 2026
        }
        est = calc.calculate(client)
        assert est.yearly_contribution["tjanste"] == 22_000


# ---------------------------------------------------------------------------
# PA16 (mixed)
# ---------------------------------------------------------------------------


class TestPA16:
    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_pa16_includes_note_about_mixed(self, _mock, calc: PensionCalculator):
        """PA16 is mixed (dc + db) → should include a note about avdelning 2."""
        client = {
            "annual_income": "500000",
            "collective_agreement": "PA16",
            "date_of_birth": "1980-01-01",
        }
        est = calc.calculate(client)
        assert any("avd 1" in n or "avd 2" in n or "avdelning" in n.lower() for n in est.notes)


# ---------------------------------------------------------------------------
# Edge cases: missing data
# ---------------------------------------------------------------------------


class TestEdgeCases:
    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_no_income(self, _mock, calc: PensionCalculator):
        """Missing income → allman and tjanste should be None, notes should explain."""
        client = {
            "collective_agreement": "ITP1",
            "date_of_birth": "1980-05-15",
        }
        est = calc.calculate(client)
        assert est.yearly_contribution["allman"] is None
        assert est.yearly_contribution["tjanste"] is None
        assert est.salary_exchange_potential is None
        assert any("saknas" in n.lower() for n in est.notes)

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_no_agreement(self, _mock, calc: PensionCalculator):
        """Missing collective agreement → tjanste None, allman still computed."""
        client = {
            "annual_income": "500000",
            "date_of_birth": "1985-01-01",
        }
        est = calc.calculate(client)
        assert est.yearly_contribution["allman"] is not None
        assert est.yearly_contribution["tjanste"] is None

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_unknown_agreement(self, _mock, calc: PensionCalculator):
        """Unknown agreement string → tjanste None, note about unknown."""
        client = {
            "annual_income": "500000",
            "collective_agreement": "UNKNOWN_AGREEMENT",
            "date_of_birth": "1985-01-01",
        }
        est = calc.calculate(client)
        assert est.yearly_contribution["tjanste"] is None
        assert any("UNKNOWN_AGREEMENT" in n for n in est.notes)

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_empty_client_dict(self, _mock, calc: PensionCalculator):
        """Completely empty client dict → should not crash."""
        est = calc.calculate({})
        assert isinstance(est, PensionEstimate)
        assert est.yearly_contribution["allman"] is None
        assert est.yearly_contribution["tjanste"] is None
        assert est.yearly_contribution["privat"] is None
        assert est.salary_exchange_potential is None

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_privat_always_none(self, _mock, calc: PensionCalculator):
        """Private pension savings cannot be computed → always None."""
        client = {
            "annual_income": "650000",
            "collective_agreement": "ITP1",
            "date_of_birth": "1980-05-15",
        }
        est = calc.calculate(client)
        assert est.yearly_contribution["privat"] is None

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_income_as_integer(self, _mock, calc: PensionCalculator):
        """Income passed as int (not string) should still work."""
        client = {
            "annual_income": 650000,
            "collective_agreement": "ITP1",
            "date_of_birth": "1980-05-15",
        }
        est = calc.calculate(client)
        assert est.yearly_contribution["tjanste"] == 35_115

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_income_as_invalid_string(self, _mock, calc: PensionCalculator):
        """Non-numeric income string → treated as missing."""
        client = {
            "annual_income": "not_a_number",
            "collective_agreement": "ITP1",
            "date_of_birth": "1980-05-15",
        }
        est = calc.calculate(client)
        assert est.yearly_contribution["allman"] is None
        assert est.yearly_contribution["tjanste"] is None


# ---------------------------------------------------------------------------
# Salary exchange
# ---------------------------------------------------------------------------


class TestSalaryExchange:
    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_salary_exchange_above_breakpoint(self, _mock, calc: PensionCalculator):
        """650k > 613,900 breakpoint → marginal tax = 32% + 20% = 52%.
        Exchange: 650,000 × 5% = 32,500
        Lost net: 32,500 × 0.48 = 15,600
        Employer pension: 32,500 × 1.06 = 34,450
        Net benefit: 34,450 - 15,600 = 18,850
        """
        client = {"annual_income": "650000", "collective_agreement": "ITP1"}
        est = calc.calculate(client)
        se = est.salary_exchange_potential
        assert se is not None
        assert se["exchange_amount_sek"] == 32_500
        assert se["marginal_tax_rate"] == pytest.approx(0.52)
        assert se["income_above_breakpoint"] is True
        assert se["lost_net_income"] == 15_600
        assert se["employer_pension_contribution"] == 34_450
        assert se["net_benefit_sek"] == 18_850

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_salary_exchange_below_breakpoint(self, _mock, calc: PensionCalculator):
        """500k < 613,900 breakpoint → marginal tax = 32% (municipal only).
        Exchange: 500,000 × 5% = 25,000
        Lost net: 25,000 × 0.68 = 17,000
        Employer pension: 25,000 × 1.06 = 26,500
        Net benefit: 26,500 - 17,000 = 9,500
        """
        client = {"annual_income": "500000", "collective_agreement": "ITP1"}
        est = calc.calculate(client)
        se = est.salary_exchange_potential
        assert se is not None
        assert se["marginal_tax_rate"] == pytest.approx(0.32)
        assert se["income_above_breakpoint"] is False
        assert se["lost_net_income"] == 17_000
        assert se["net_benefit_sek"] == 9_500

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_salary_exchange_not_computed_without_income(self, _mock, calc: PensionCalculator):
        """No income → salary exchange potential should be None."""
        client = {"collective_agreement": "ITP1"}
        est = calc.calculate(client)
        assert est.salary_exchange_potential is None


# ---------------------------------------------------------------------------
# Projected monthly pension
# ---------------------------------------------------------------------------


class TestProjectedPension:
    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_projected_pension_computed_with_full_data(self, _mock, calc: PensionCalculator):
        """With income, age, and retirement_age, a projection should be produced."""
        client = {
            "annual_income": "650000",
            "collective_agreement": "ITP1",
            "date_of_birth": "1980-05-15",
            "desired_retirement_age": 65,
        }
        est = calc.calculate(client)
        assert est.projected_monthly_pension is not None
        assert est.projected_monthly_pension > 0

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_no_projected_pension_without_retirement_age(self, _mock, calc: PensionCalculator):
        """Missing retirement age → no projection."""
        client = {
            "annual_income": "650000",
            "collective_agreement": "ITP1",
            "date_of_birth": "1980-05-15",
        }
        est = calc.calculate(client)
        assert est.projected_monthly_pension is None

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_no_projected_pension_without_dob(self, _mock, calc: PensionCalculator):
        """Missing date of birth → no projection."""
        client = {
            "annual_income": "650000",
            "collective_agreement": "ITP1",
            "desired_retirement_age": 65,
        }
        est = calc.calculate(client)
        assert est.projected_monthly_pension is None

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_projected_pension_already_retired(self, _mock, calc: PensionCalculator):
        """Client past retirement age (years_to_retirement <= 0) → no projection."""
        client = {
            "annual_income": "650000",
            "collective_agreement": "ITP1",
            "date_of_birth": "1950-01-01",  # 76 in 2026
            "desired_retirement_age": 65,
        }
        est = calc.calculate(client)
        assert est.projected_monthly_pension is None


# ---------------------------------------------------------------------------
# IBB is included in output
# ---------------------------------------------------------------------------


class TestOutputStructure:
    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_ibb_in_output(self, _mock, calc: PensionCalculator):
        """The IBB used should be included in the output for traceability."""
        est = calc.calculate({"annual_income": "500000", "collective_agreement": "ITP1"})
        assert est.ibb == 83_600

    @patch.object(PensionCalculator, "_current_year", return_value=2026)
    def test_rates_in_output(self, _mock, calc: PensionCalculator):
        """Contribution rates config should be in output for transparency."""
        est = calc.calculate({"annual_income": "500000", "collective_agreement": "ITP1"})
        assert est.contribution_rates["year"] == 2026
        assert est.contribution_rates["allman_pension"]["inkomstpension"] == 0.16
        assert est.contribution_rates["allman_pension"]["premiepension"] == 0.025
