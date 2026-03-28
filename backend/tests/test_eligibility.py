"""Tests for the eligibility checker.

Verifies agreement-provider mappings and recommendation type eligibility rules
against published data from Collectum, Fora, SKR, and SPV.
"""

import pytest
from unittest.mock import patch
from datetime import date

from app.services.eligibility import (
    EligibilityChecker,
    EligibilityResult,
    AGREEMENT_PROVIDERS,
)


@pytest.fixture
def checker() -> EligibilityChecker:
    return EligibilityChecker()


# ---------------------------------------------------------------------------
# Agreement → provider mapping
# ---------------------------------------------------------------------------


class TestProviderMapping:
    def test_itp1_providers_include_key_names(self, checker: EligibilityChecker):
        """ITP1 via Collectum: Alecta (default), AMF, SPP, Skandia, etc."""
        result = checker.check(
            {"collective_agreement": "ITP1", "employment_status": "employed"},
            "pension_review",
        )
        for provider in ["Alecta", "AMF", "SPP", "Skandia", "Folksam", "Länsförsäkringar"]:
            assert provider in result.eligible_providers

    def test_saf_lo_providers_include_key_names(self, checker: EligibilityChecker):
        """SAF-LO via Fora: AMF (default), Folksam, Skandia, Swedbank, etc."""
        result = checker.check(
            {"collective_agreement": "SAF_LO", "employment_status": "employed"},
            "pension_review",
        )
        for provider in ["AMF", "Folksam", "Skandia", "Swedbank", "Handelsbanken"]:
            assert provider in result.eligible_providers

    def test_itp2_providers_alecta_only(self, checker: EligibilityChecker):
        """ITP2: Alecta mandatory for the defined benefit portion."""
        result = checker.check(
            {"collective_agreement": "ITP2", "employment_status": "employed"},
            "pension_review",
        )
        assert "Alecta" in result.eligible_providers
        assert len(result.eligible_providers) == 1

    def test_pa16_providers_include_kapan(self, checker: EligibilityChecker):
        """PA16 via SPV: Kåpan is the provider."""
        result = checker.check(
            {"collective_agreement": "PA16", "employment_status": "employed"},
            "pension_review",
        )
        assert "Kåpan" in result.eligible_providers

    def test_kap_kl_no_individual_providers(self, checker: EligibilityChecker):
        """KAP-KL: employer-managed, no individual provider choice."""
        result = checker.check(
            {"collective_agreement": "KAP_KL", "employment_status": "employed"},
            "pension_review",
        )
        assert result.eligible_providers == []

    def test_unknown_agreement_no_providers(self, checker: EligibilityChecker):
        """Unknown agreement → empty provider list."""
        result = checker.check(
            {"collective_agreement": "UNKNOWN", "employment_status": "employed"},
            "pension_review",
        )
        assert result.eligible_providers == []

    def test_missing_agreement_no_providers(self, checker: EligibilityChecker):
        """No collective_agreement key → empty provider list."""
        result = checker.check(
            {"employment_status": "employed"},
            "pension_review",
        )
        assert result.eligible_providers == []


# ---------------------------------------------------------------------------
# Salary exchange eligibility
# ---------------------------------------------------------------------------


class TestSalaryExchange:
    def test_employed_itp1_sufficient_income_eligible(self, checker: EligibilityChecker):
        """Employed + ITP1 + income > 300k → eligible for salary exchange."""
        result = checker.check(
            {
                "collective_agreement": "ITP1",
                "employment_status": "employed",
                "annual_income": "650000",
            },
            "salary_exchange",
        )
        assert result.eligible is True

    def test_self_employed_not_eligible(self, checker: EligibilityChecker):
        """Self-employed → not eligible for salary exchange."""
        result = checker.check(
            {
                "collective_agreement": "ITP1",
                "employment_status": "self_employed",
                "annual_income": "650000",
            },
            "salary_exchange",
        )
        assert result.eligible is False

    def test_retired_not_eligible(self, checker: EligibilityChecker):
        """Retired → not eligible for salary exchange."""
        result = checker.check(
            {
                "collective_agreement": "ITP1",
                "employment_status": "retired",
                "annual_income": "650000",
            },
            "salary_exchange",
        )
        assert result.eligible is False

    def test_pa16_not_eligible_for_salary_exchange(self, checker: EligibilityChecker):
        """PA16 is not in the salary exchange agreements set → not eligible."""
        result = checker.check(
            {
                "collective_agreement": "PA16",
                "employment_status": "employed",
                "annual_income": "650000",
            },
            "salary_exchange",
        )
        assert result.eligible is False

    def test_low_income_not_eligible(self, checker: EligibilityChecker):
        """Income below 300k threshold → not eligible."""
        result = checker.check(
            {
                "collective_agreement": "ITP1",
                "employment_status": "employed",
                "annual_income": "200000",
            },
            "salary_exchange",
        )
        assert result.eligible is False

    def test_missing_income_still_eligible_but_warned(self, checker: EligibilityChecker):
        """No income data → eligible (employment + agreement OK) but with warning."""
        result = checker.check(
            {
                "collective_agreement": "ITP1",
                "employment_status": "employed",
            },
            "salary_exchange",
        )
        assert result.eligible is True
        assert any("saknas" in w.lower() for w in result.warnings)

    def test_near_retirement_warning(self, checker: EligibilityChecker):
        """Employed + ITP1 but 1 year to retirement → eligible with warning."""
        result = checker.check(
            {
                "collective_agreement": "ITP1",
                "employment_status": "employed",
                "annual_income": "650000",
                "date_of_birth": "1962-01-01",  # ~64 in 2026
                "desired_retirement_age": 65,
            },
            "salary_exchange",
        )
        assert result.eligible is True
        assert any("kort tid" in w.lower() for w in result.warnings)

    def test_saf_lo_eligible(self, checker: EligibilityChecker):
        """SAF-LO is in the salary exchange set → eligible."""
        result = checker.check(
            {
                "collective_agreement": "SAF_LO",
                "employment_status": "employed",
                "annual_income": "400000",
            },
            "salary_exchange",
        )
        assert result.eligible is True


# ---------------------------------------------------------------------------
# Transfer advice eligibility
# ---------------------------------------------------------------------------


class TestTransferAdvice:
    def test_itp1_eligible_for_transfer(self, checker: EligibilityChecker):
        """ITP1 is a DC agreement → transfer is possible."""
        result = checker.check(
            {"collective_agreement": "ITP1", "employment_status": "employed"},
            "transfer_advice",
        )
        assert result.eligible is True

    def test_itp2_not_eligible_for_transfer(self, checker: EligibilityChecker):
        """ITP2 is defined benefit → transfer of the main part not possible."""
        result = checker.check(
            {"collective_agreement": "ITP2", "employment_status": "employed"},
            "transfer_advice",
        )
        assert result.eligible is False
        assert any("ITPK" in w for w in result.warnings)

    def test_no_agreement_not_eligible_for_transfer(self, checker: EligibilityChecker):
        """No agreement → cannot assess transferability."""
        result = checker.check(
            {"employment_status": "employed"},
            "transfer_advice",
        )
        assert result.eligible is False

    def test_transfer_always_warns_about_fees(self, checker: EligibilityChecker):
        """Transfer advice should always warn about potential fees."""
        result = checker.check(
            {"collective_agreement": "ITP1", "employment_status": "employed"},
            "transfer_advice",
        )
        assert any("avgift" in w.lower() for w in result.warnings)


# ---------------------------------------------------------------------------
# Survivor protection eligibility
# ---------------------------------------------------------------------------


class TestSurvivorProtection:
    def test_always_eligible(self, checker: EligibilityChecker):
        """Survivor protection is always relevant."""
        result = checker.check(
            {"collective_agreement": "ITP1", "employment_status": "employed"},
            "survivor_protection",
        )
        assert result.eligible is True

    def test_eligible_without_agreement(self, checker: EligibilityChecker):
        """Even without agreement → still eligible."""
        result = checker.check(
            {"employment_status": "employed"},
            "survivor_protection",
        )
        assert result.eligible is True

    def test_itp_includes_family_protection_warning(self, checker: EligibilityChecker):
        """ITP agreements include built-in family protection → warn to check."""
        result = checker.check(
            {"collective_agreement": "ITP1", "employment_status": "employed"},
            "survivor_protection",
        )
        assert any("familjeskydd" in w.lower() or "alecta" in w.lower() for w in result.warnings)

    def test_coverage_change_alias(self, checker: EligibilityChecker):
        """coverage_change should route to survivor_protection check."""
        result = checker.check(
            {"collective_agreement": "SAF_LO", "employment_status": "employed"},
            "coverage_change",
        )
        assert result.eligible is True


# ---------------------------------------------------------------------------
# Decumulation eligibility
# ---------------------------------------------------------------------------


class TestDecumulation:
    def test_retired_eligible(self, checker: EligibilityChecker):
        """Retired client → eligible for decumulation."""
        result = checker.check(
            {
                "collective_agreement": "ITP1",
                "employment_status": "retired",
            },
            "decumulation",
        )
        assert result.eligible is True

    def test_young_employed_not_eligible(self, checker: EligibilityChecker):
        """30-year-old employed, retirement at 65 → 35 years out, not eligible."""
        result = checker.check(
            {
                "collective_agreement": "ITP1",
                "employment_status": "employed",
                "date_of_birth": "1996-01-01",  # ~30 in 2026
                "desired_retirement_age": 65,
            },
            "decumulation",
        )
        assert result.eligible is False

    def test_near_retirement_eligible(self, checker: EligibilityChecker):
        """62-year-old with retirement at 65 → 3 years out, eligible."""
        result = checker.check(
            {
                "collective_agreement": "ITP1",
                "employment_status": "employed",
                "date_of_birth": "1964-01-01",  # ~62 in 2026
                "desired_retirement_age": 65,
            },
            "decumulation",
        )
        assert result.eligible is True

    def test_old_client_no_retirement_age(self, checker: EligibilityChecker):
        """Age 62 but no retirement age set → eligible (age >= 60 fallback)."""
        result = checker.check(
            {
                "collective_agreement": "ITP1",
                "employment_status": "employed",
                "date_of_birth": "1964-01-01",  # ~62 in 2026
            },
            "decumulation",
        )
        assert result.eligible is True
        assert any("saknas" in w.lower() for w in result.warnings)

    def test_withdrawal_plan_alias(self, checker: EligibilityChecker):
        """withdrawal_plan should route to decumulation check."""
        result = checker.check(
            {"employment_status": "retired", "collective_agreement": "ITP1"},
            "withdrawal_plan",
        )
        assert result.eligible is True

    def test_eligible_includes_withdrawal_warning(self, checker: EligibilityChecker):
        """Eligible decumulation should warn about withdrawal order tax effects."""
        result = checker.check(
            {"employment_status": "retired", "collective_agreement": "ITP1"},
            "decumulation",
        )
        assert any("uttagsordning" in w.lower() or "skatteeffekt" in w.lower() for w in result.warnings)


# ---------------------------------------------------------------------------
# Generic / pension_review
# ---------------------------------------------------------------------------


class TestGenericRecommendation:
    def test_pension_review_always_eligible(self, checker: EligibilityChecker):
        """Pension review has no specific eligibility restrictions."""
        result = checker.check(
            {"collective_agreement": "ITP1", "employment_status": "employed"},
            "pension_review",
        )
        assert result.eligible is True

    def test_unknown_type_defaults_to_generic(self, checker: EligibilityChecker):
        """Unknown recommendation type → generic check, always eligible."""
        result = checker.check(
            {"collective_agreement": "ITP1", "employment_status": "employed"},
            "some_unknown_type",
        )
        assert result.eligible is True

    def test_reasons_always_populated(self, checker: EligibilityChecker):
        """Every result should have at least one reason."""
        result = checker.check(
            {"collective_agreement": "ITP1", "employment_status": "employed"},
            "pension_review",
        )
        assert len(result.reasons) >= 1


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_empty_client_dict(self, checker: EligibilityChecker):
        """Empty client dict → should not crash."""
        result = checker.check({}, "pension_review")
        assert isinstance(result, EligibilityResult)
        assert result.eligible is True  # generic allows it

    def test_salary_exchange_empty_client(self, checker: EligibilityChecker):
        """Salary exchange with empty client → not eligible (no employment, no agreement)."""
        result = checker.check({}, "salary_exchange")
        assert result.eligible is False

    def test_recommendation_type_case_insensitive(self, checker: EligibilityChecker):
        """Recommendation type should be case-insensitive."""
        result = checker.check(
            {
                "collective_agreement": "ITP1",
                "employment_status": "employed",
                "annual_income": "650000",
            },
            "SALARY_EXCHANGE",
        )
        assert result.eligible is True

    def test_recommendation_type_whitespace_trimmed(self, checker: EligibilityChecker):
        """Recommendation type should be trimmed."""
        result = checker.check(
            {
                "collective_agreement": "ITP1",
                "employment_status": "employed",
                "annual_income": "650000",
            },
            "  salary_exchange  ",
        )
        assert result.eligible is True
