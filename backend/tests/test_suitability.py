"""Tests for the deterministic suitability scoring engine.

Verifies the five-factor weighted scoring: risk profile match (0.25),
age appropriateness (0.20), income adequacy (0.15), agreement eligibility (0.20),
data completeness (0.20). Weights sum to 1.0.
"""

import pytest
from unittest.mock import patch

from app.services.suitability import (
    SuitabilityEngine,
    SuitabilityResult,
    SuitabilityFactor,
    FACTOR_WEIGHTS,
    COMPLETENESS_FIELDS,
)


@pytest.fixture
def engine() -> SuitabilityEngine:
    return SuitabilityEngine()


def _get_factor(result: SuitabilityResult, name: str) -> SuitabilityFactor:
    """Helper to extract a specific factor from the result."""
    for f in result.factors:
        if f.name == name:
            return f
    raise ValueError(f"Factor '{name}' not found in result")


# ---------------------------------------------------------------------------
# Weights configuration
# ---------------------------------------------------------------------------


class TestWeights:
    def test_weights_sum_to_one(self):
        """Factor weights must sum to exactly 1.0."""
        assert sum(FACTOR_WEIGHTS.values()) == pytest.approx(1.0)

    def test_five_factors_returned(self, engine: SuitabilityEngine):
        """Score should always return exactly 5 factors."""
        client = {"collective_agreement": "ITP1", "employment_status": "employed"}
        result = engine.score(client, "pension_review", None)
        assert len(result.factors) == 5


# ---------------------------------------------------------------------------
# Full data client
# ---------------------------------------------------------------------------


class TestFullDataClient:
    """Client with all fields filled should score well."""

    FULL_CLIENT = {
        "name": "Test Testsson",
        "date_of_birth": "1980-05-15",
        "employment_status": "employed",
        "employer_name": "ACME AB",
        "collective_agreement": "ITP1",
        "annual_income": "650000",
        "risk_profile": "moderate",
        "desired_retirement_age": 65,
    }

    @patch.object(SuitabilityEngine, "_client_age", return_value=45)
    def test_data_completeness_all_filled(self, _mock, engine: SuitabilityEngine):
        """All 7 completeness fields filled → score = 1.0."""
        result = engine.score(self.FULL_CLIENT, "pension_review", None)
        factor = _get_factor(result, "data_completeness")
        assert factor.score == pytest.approx(1.0)

    @patch.object(SuitabilityEngine, "_client_age", return_value=45)
    def test_overall_score_reasonable(self, _mock, engine: SuitabilityEngine):
        """Full data client with known agreement → score should be >= 0.6."""
        result = engine.score(self.FULL_CLIENT, "pension_review", None)
        assert result.total_score >= 0.6

    @patch.object(SuitabilityEngine, "_client_age", return_value=45)
    def test_agreement_eligibility_known_agreement(self, _mock, engine: SuitabilityEngine):
        """ITP1 for pension_review → agreement eligibility = 1.0."""
        result = engine.score(self.FULL_CLIENT, "pension_review", None)
        factor = _get_factor(result, "agreement_eligibility")
        assert factor.score == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Minimal data client
# ---------------------------------------------------------------------------


class TestMinimalDataClient:
    """Client with only a few fields → low data completeness, lower score."""

    MINIMAL_CLIENT = {
        "name": "Minimal Testsson",
        "date_of_birth": "1985-06-15",
        "collective_agreement": "ITP1",
        "employment_status": "employed",
    }

    @patch.object(SuitabilityEngine, "_client_age", return_value=40)
    def test_data_completeness_partial(self, _mock, engine: SuitabilityEngine):
        """MINIMAL_CLIENT has name, date_of_birth, collective_agreement filled.
        employment_status is NOT in COMPLETENESS_FIELDS, so 3/7 ≈ 0.4286.
        """
        result = engine.score(self.MINIMAL_CLIENT, "pension_review", None)
        factor = _get_factor(result, "data_completeness")
        assert factor.score == pytest.approx(3 / 7, abs=0.01)

    @patch.object(SuitabilityEngine, "_client_age", return_value=40)
    def test_income_adequacy_missing_income(self, _mock, engine: SuitabilityEngine):
        """No income → income adequacy defaults to 0.5."""
        result = engine.score(self.MINIMAL_CLIENT, "pension_review", None)
        factor = _get_factor(result, "income_adequacy")
        assert factor.score == pytest.approx(0.5)

    @patch.object(SuitabilityEngine, "_client_age", return_value=40)
    def test_risk_profile_missing(self, _mock, engine: SuitabilityEngine):
        """No risk profile → risk profile match defaults to 0.5."""
        result = engine.score(self.MINIMAL_CLIENT, "pension_review", None)
        factor = _get_factor(result, "risk_profile_match")
        assert factor.score == pytest.approx(0.5)

    @patch.object(SuitabilityEngine, "_client_age", return_value=40)
    def test_overall_score_lower_than_full(self, _mock, engine: SuitabilityEngine):
        """Minimal client should score lower than full data client."""
        full = {
            "name": "Test",
            "date_of_birth": "1985-06-15",
            "employment_status": "employed",
            "employer_name": "ACME",
            "collective_agreement": "ITP1",
            "annual_income": "650000",
            "risk_profile": "moderate",
            "desired_retirement_age": 65,
        }
        full_result = engine.score(full, "pension_review", None)
        min_result = engine.score(self.MINIMAL_CLIENT, "pension_review", None)
        assert min_result.total_score < full_result.total_score


# ---------------------------------------------------------------------------
# Risk profile matching
# ---------------------------------------------------------------------------


class TestRiskProfileMatch:
    def test_no_scenarios_defaults_to_half(self, engine: SuitabilityEngine):
        """No scenarios → risk match factor = 0.5."""
        client = {"risk_profile": "moderate"}
        result = engine.score(client, "pension_review", None)
        factor = _get_factor(result, "risk_profile_match")
        assert factor.score == pytest.approx(0.5)

    def test_matching_risk_level(self, engine: SuitabilityEngine):
        """Moderate profile + moderate scenario → full match (1.0)."""
        client = {"risk_profile": "moderate"}
        scenarios = [{"name": "Balanserad portfölj", "description": "Moderate risk"}]
        result = engine.score(client, "pension_review", scenarios)
        factor = _get_factor(result, "risk_profile_match")
        assert factor.score == pytest.approx(1.0)

    def test_slight_mismatch(self, engine: SuitabilityEngine):
        """Low-risk profile + moderate scenario → mismatch of 1, score 0.7."""
        client = {"risk_profile": "low"}
        scenarios = [{"name": "Balanserad portfölj", "description": "Moderate risk level"}]
        result = engine.score(client, "pension_review", scenarios)
        factor = _get_factor(result, "risk_profile_match")
        assert factor.score == pytest.approx(0.7)

    def test_large_mismatch(self, engine: SuitabilityEngine):
        """Low-risk profile + aggressive scenario → mismatch >= 2, score 0.3."""
        client = {"risk_profile": "low"}
        scenarios = [{"name": "Aggressiv tillväxt", "description": "Hög risk exponering"}]
        result = engine.score(client, "pension_review", scenarios)
        factor = _get_factor(result, "risk_profile_match")
        assert factor.score == pytest.approx(0.3)

    def test_no_risk_profile_defaults_to_half(self, engine: SuitabilityEngine):
        """No risk_profile key → 0.5 regardless of scenarios."""
        client = {}
        scenarios = [{"name": "Aggressiv", "description": ""}]
        result = engine.score(client, "pension_review", scenarios)
        factor = _get_factor(result, "risk_profile_match")
        assert factor.score == pytest.approx(0.5)

    def test_scenario_without_risk_keywords_defaults_moderate(self, engine: SuitabilityEngine):
        """Scenario with no risk keywords → defaults to moderate (level 2).
        Moderate profile (level 2) + default moderate → match (1.0).
        """
        client = {"risk_profile": "moderate"}
        scenarios = [{"name": "Scenario A", "description": "Standard investment"}]
        result = engine.score(client, "pension_review", scenarios)
        factor = _get_factor(result, "risk_profile_match")
        assert factor.score == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Age appropriateness
# ---------------------------------------------------------------------------


class TestAgeAppropriateness:
    @patch.object(SuitabilityEngine, "_client_age", return_value=63)
    def test_salary_exchange_near_retirement_low_score(self, _mock, engine: SuitabilityEngine):
        """63-year-old, retirement at 65 → 2 years → score = 0.2."""
        client = {"date_of_birth": "1963-01-01", "desired_retirement_age": 65}
        result = engine.score(client, "salary_exchange", None)
        factor = _get_factor(result, "age_appropriateness")
        assert factor.score == pytest.approx(0.2)

    @patch.object(SuitabilityEngine, "_client_age", return_value=45)
    def test_pension_review_mid_career(self, _mock, engine: SuitabilityEngine):
        """45-year-old, retirement at 65 → 20 years → generic score 0.8."""
        client = {"date_of_birth": "1981-01-01", "desired_retirement_age": 65}
        result = engine.score(client, "pension_review", None)
        factor = _get_factor(result, "age_appropriateness")
        assert factor.score == pytest.approx(0.8)

    @patch.object(SuitabilityEngine, "_client_age", return_value=55)
    def test_salary_exchange_10_years_out(self, _mock, engine: SuitabilityEngine):
        """55-year-old, retirement at 65 → 10 years → score = 1.0 (within 6-15 range)."""
        client = {"date_of_birth": "1971-01-01", "desired_retirement_age": 65}
        result = engine.score(client, "salary_exchange", None)
        factor = _get_factor(result, "age_appropriateness")
        assert factor.score == pytest.approx(1.0)

    @patch.object(SuitabilityEngine, "_client_age", return_value=40)
    def test_salary_exchange_25_years_out(self, _mock, engine: SuitabilityEngine):
        """40-year-old, retirement at 65 → 25 years → score = 0.9 (>15 years)."""
        client = {"date_of_birth": "1986-01-01", "desired_retirement_age": 65}
        result = engine.score(client, "salary_exchange", None)
        factor = _get_factor(result, "age_appropriateness")
        assert factor.score == pytest.approx(0.9)

    @patch.object(SuitabilityEngine, "_client_age", return_value=65)
    def test_decumulation_at_retirement_age(self, _mock, engine: SuitabilityEngine):
        """At retirement age (0 years left) → decumulation score = 1.0."""
        client = {"date_of_birth": "1961-01-01", "desired_retirement_age": 65}
        result = engine.score(client, "decumulation", None)
        factor = _get_factor(result, "age_appropriateness")
        assert factor.score == pytest.approx(1.0)

    @patch.object(SuitabilityEngine, "_client_age", return_value=35)
    def test_decumulation_far_from_retirement(self, _mock, engine: SuitabilityEngine):
        """35-year-old, retirement at 65 → 30 years → decumulation score = 0.2."""
        client = {"date_of_birth": "1991-01-01", "desired_retirement_age": 65}
        result = engine.score(client, "decumulation", None)
        factor = _get_factor(result, "age_appropriateness")
        assert factor.score == pytest.approx(0.2)

    def test_missing_age_defaults_to_half(self, engine: SuitabilityEngine):
        """Missing date_of_birth → age appropriateness defaults to 0.5."""
        client = {"desired_retirement_age": 65}
        result = engine.score(client, "pension_review", None)
        factor = _get_factor(result, "age_appropriateness")
        assert factor.score == pytest.approx(0.5)

    def test_missing_retirement_age_defaults_to_half(self, engine: SuitabilityEngine):
        """Missing desired_retirement_age → defaults to 0.5."""
        client = {"date_of_birth": "1980-01-01"}
        result = engine.score(client, "pension_review", None)
        factor = _get_factor(result, "age_appropriateness")
        assert factor.score == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# Income adequacy
# ---------------------------------------------------------------------------


class TestIncomeAdequacy:
    def test_high_income_salary_exchange(self, engine: SuitabilityEngine):
        """Income 650k >= 600k threshold for salary exchange → score = 1.0."""
        client = {"annual_income": "650000"}
        result = engine.score(client, "salary_exchange", None)
        factor = _get_factor(result, "income_adequacy")
        assert factor.score == pytest.approx(1.0)

    def test_moderate_income_salary_exchange(self, engine: SuitabilityEngine):
        """Income 400k: >= 300k but < 600k for salary exchange → score = 0.7."""
        client = {"annual_income": "400000"}
        result = engine.score(client, "salary_exchange", None)
        factor = _get_factor(result, "income_adequacy")
        assert factor.score == pytest.approx(0.7)

    def test_low_income_salary_exchange(self, engine: SuitabilityEngine):
        """Income 200k < 300k min for salary exchange → score = 0.2."""
        client = {"annual_income": "200000"}
        result = engine.score(client, "salary_exchange", None)
        factor = _get_factor(result, "income_adequacy")
        assert factor.score == pytest.approx(0.2)

    def test_high_income_generic(self, engine: SuitabilityEngine):
        """Income 650k >= 500k for generic → score = 0.9."""
        client = {"annual_income": "650000"}
        result = engine.score(client, "pension_review", None)
        factor = _get_factor(result, "income_adequacy")
        assert factor.score == pytest.approx(0.9)

    def test_low_income_generic(self, engine: SuitabilityEngine):
        """Income 100k < 150k for generic → score = 0.3."""
        client = {"annual_income": "100000"}
        result = engine.score(client, "pension_review", None)
        factor = _get_factor(result, "income_adequacy")
        assert factor.score == pytest.approx(0.3)

    def test_missing_income(self, engine: SuitabilityEngine):
        """No income → defaults to 0.5."""
        client = {}
        result = engine.score(client, "pension_review", None)
        factor = _get_factor(result, "income_adequacy")
        assert factor.score == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# Agreement eligibility factor
# ---------------------------------------------------------------------------


class TestAgreementEligibilityFactor:
    def test_salary_exchange_itp1_employed(self, engine: SuitabilityEngine):
        """ITP1 + employed for salary_exchange → eligibility factor = 1.0."""
        client = {"collective_agreement": "ITP1", "employment_status": "employed"}
        result = engine.score(client, "salary_exchange", None)
        factor = _get_factor(result, "agreement_eligibility")
        assert factor.score == pytest.approx(1.0)

    def test_salary_exchange_pa16(self, engine: SuitabilityEngine):
        """PA16 for salary_exchange → eligibility factor = 0.0 (not in set)."""
        client = {"collective_agreement": "PA16", "employment_status": "employed"}
        result = engine.score(client, "salary_exchange", None)
        factor = _get_factor(result, "agreement_eligibility")
        assert factor.score == pytest.approx(0.0)

    def test_salary_exchange_itp1_not_employed(self, engine: SuitabilityEngine):
        """ITP1 but self_employed for salary_exchange → eligibility factor = 0.5."""
        client = {"collective_agreement": "ITP1", "employment_status": "self_employed"}
        result = engine.score(client, "salary_exchange", None)
        factor = _get_factor(result, "agreement_eligibility")
        assert factor.score == pytest.approx(0.5)

    def test_no_agreement(self, engine: SuitabilityEngine):
        """No collective agreement → eligibility factor = 0.3."""
        client = {"employment_status": "employed"}
        result = engine.score(client, "pension_review", None)
        factor = _get_factor(result, "agreement_eligibility")
        assert factor.score == pytest.approx(0.3)

    def test_transfer_itp2(self, engine: SuitabilityEngine):
        """ITP2 for transfer → eligibility factor = 0.2 (defined benefit)."""
        client = {"collective_agreement": "ITP2", "employment_status": "employed"}
        result = engine.score(client, "transfer_advice", None)
        factor = _get_factor(result, "agreement_eligibility")
        assert factor.score == pytest.approx(0.2)

    def test_transfer_itp1(self, engine: SuitabilityEngine):
        """ITP1 for transfer → eligibility factor = 1.0 (known DC agreement)."""
        client = {"collective_agreement": "ITP1", "employment_status": "employed"}
        result = engine.score(client, "transfer_advice", None)
        factor = _get_factor(result, "agreement_eligibility")
        assert factor.score == pytest.approx(1.0)

    def test_none_string_agreement(self, engine: SuitabilityEngine):
        """Agreement value 'none' → treated as missing, score = 0.3."""
        client = {"collective_agreement": "none", "employment_status": "employed"}
        result = engine.score(client, "pension_review", None)
        factor = _get_factor(result, "agreement_eligibility")
        assert factor.score == pytest.approx(0.3)


# ---------------------------------------------------------------------------
# Data completeness
# ---------------------------------------------------------------------------


class TestDataCompleteness:
    def test_all_fields_filled(self, engine: SuitabilityEngine):
        """All 7 fields filled → score = 1.0."""
        client = {
            "name": "Test",
            "date_of_birth": "1980-01-01",
            "employer_name": "ACME",
            "collective_agreement": "ITP1",
            "annual_income": "500000",
            "risk_profile": "moderate",
            "desired_retirement_age": 65,
        }
        result = engine.score(client, "pension_review", None)
        factor = _get_factor(result, "data_completeness")
        assert factor.score == pytest.approx(1.0)

    def test_no_fields_filled(self, engine: SuitabilityEngine):
        """Empty client → score = 0.0."""
        result = engine.score({}, "pension_review", None)
        factor = _get_factor(result, "data_completeness")
        assert factor.score == pytest.approx(0.0)

    def test_half_fields_filled(self, engine: SuitabilityEngine):
        """3 out of 7 fields → score ≈ 3/7."""
        client = {
            "name": "Test",
            "date_of_birth": "1980-01-01",
            "collective_agreement": "ITP1",
        }
        result = engine.score(client, "pension_review", None)
        factor = _get_factor(result, "data_completeness")
        assert factor.score == pytest.approx(3 / 7, abs=0.01)

    def test_empty_string_not_counted(self, engine: SuitabilityEngine):
        """Empty string values should not count as filled."""
        client = {
            "name": "",
            "date_of_birth": "1980-01-01",
            "employer_name": "",
            "collective_agreement": "ITP1",
            "annual_income": "",
            "risk_profile": "",
            "desired_retirement_age": 65,
        }
        result = engine.score(client, "pension_review", None)
        factor = _get_factor(result, "data_completeness")
        # Only date_of_birth, collective_agreement, desired_retirement_age → 3/7
        assert factor.score == pytest.approx(3 / 7, abs=0.01)

    def test_none_value_not_counted(self, engine: SuitabilityEngine):
        """None values should not count as filled."""
        client = {
            "name": "Test",
            "date_of_birth": "1980-01-01",
            "employer_name": None,
            "collective_agreement": "ITP1",
            "annual_income": None,
            "risk_profile": None,
            "desired_retirement_age": None,
        }
        result = engine.score(client, "pension_review", None)
        factor = _get_factor(result, "data_completeness")
        # name, date_of_birth, collective_agreement → 3/7
        assert factor.score == pytest.approx(3 / 7, abs=0.01)


# ---------------------------------------------------------------------------
# Grade boundaries
# ---------------------------------------------------------------------------


class TestGradeBoundaries:
    def test_grade_high(self, engine: SuitabilityEngine):
        """Score >= 0.7 → grade 'high'."""
        assert engine._compute_grade(0.7) == "high"
        assert engine._compute_grade(0.85) == "high"
        assert engine._compute_grade(1.0) == "high"

    def test_grade_moderate(self, engine: SuitabilityEngine):
        """Score 0.4–0.69 → grade 'moderate'."""
        assert engine._compute_grade(0.4) == "moderate"
        assert engine._compute_grade(0.55) == "moderate"
        assert engine._compute_grade(0.69) == "moderate"

    def test_grade_low(self, engine: SuitabilityEngine):
        """Score < 0.4 → grade 'low'."""
        assert engine._compute_grade(0.0) == "low"
        assert engine._compute_grade(0.2) == "low"
        assert engine._compute_grade(0.39) == "low"

    def test_grade_boundary_exact_0_7(self, engine: SuitabilityEngine):
        """Exactly 0.7 → 'high' (inclusive boundary)."""
        assert engine._compute_grade(0.7) == "high"

    def test_grade_boundary_exact_0_4(self, engine: SuitabilityEngine):
        """Exactly 0.4 → 'moderate' (inclusive boundary)."""
        assert engine._compute_grade(0.4) == "moderate"

    def test_grade_boundary_just_below_0_7(self, engine: SuitabilityEngine):
        """0.6999 → 'moderate'."""
        assert engine._compute_grade(0.6999) == "moderate"

    def test_grade_boundary_just_below_0_4(self, engine: SuitabilityEngine):
        """0.3999 → 'low'."""
        assert engine._compute_grade(0.3999) == "low"


# ---------------------------------------------------------------------------
# Total score calculation
# ---------------------------------------------------------------------------


class TestTotalScore:
    def test_score_between_0_and_1(self, engine: SuitabilityEngine):
        """Total score must always be in [0, 1]."""
        client = {
            "name": "Test",
            "date_of_birth": "1980-01-01",
            "collective_agreement": "ITP1",
            "employment_status": "employed",
            "annual_income": "650000",
            "risk_profile": "moderate",
            "desired_retirement_age": 65,
        }
        result = engine.score(client, "pension_review", None)
        assert 0.0 <= result.total_score <= 1.0

    def test_empty_client_score_in_range(self, engine: SuitabilityEngine):
        """Even empty client → score should be in [0, 1]."""
        result = engine.score({}, "pension_review", None)
        assert 0.0 <= result.total_score <= 1.0

    def test_total_is_weighted_sum(self, engine: SuitabilityEngine):
        """Total score should equal the weighted sum of factor scores."""
        client = {
            "name": "Test",
            "date_of_birth": "1980-01-01",
            "collective_agreement": "ITP1",
            "employment_status": "employed",
        }
        result = engine.score(client, "pension_review", None)
        expected = sum(f.score * f.weight for f in result.factors)
        assert result.total_score == pytest.approx(expected, abs=0.001)

    def test_all_factors_have_correct_weights(self, engine: SuitabilityEngine):
        """Each factor should carry its defined weight."""
        result = engine.score(
            {"collective_agreement": "ITP1", "employment_status": "employed"},
            "pension_review",
            None,
        )
        for factor in result.factors:
            assert factor.weight == pytest.approx(FACTOR_WEIGHTS[factor.name])


# ---------------------------------------------------------------------------
# Integration-like scenarios
# ---------------------------------------------------------------------------


class TestIntegrationScenarios:
    @patch.object(SuitabilityEngine, "_client_age", return_value=63)
    def test_bad_salary_exchange_candidate(self, _mock, engine: SuitabilityEngine):
        """PA16, self-employed, low income, near retirement → low score for salary_exchange."""
        client = {
            "date_of_birth": "1963-01-01",
            "employment_status": "self_employed",
            "collective_agreement": "PA16",
            "annual_income": "200000",
            "desired_retirement_age": 65,
        }
        result = engine.score(client, "salary_exchange", None)
        # PA16 → agreement 0.0, self-employed → doesn't get 1.0 for agreement,
        # low income → 0.2, near retirement → 0.2
        assert result.total_score < 0.4
        assert result.grade == "low"

    @patch.object(SuitabilityEngine, "_client_age", return_value=45)
    def test_ideal_salary_exchange_candidate(self, _mock, engine: SuitabilityEngine):
        """ITP1, employed, high income, 20 years to retirement → high score."""
        client = {
            "name": "Ideal Testsson",
            "date_of_birth": "1981-01-01",
            "employment_status": "employed",
            "employer_name": "Big Corp AB",
            "collective_agreement": "ITP1",
            "annual_income": "800000",
            "risk_profile": "moderate",
            "desired_retirement_age": 65,
        }
        result = engine.score(client, "salary_exchange", None)
        assert result.total_score >= 0.7
        assert result.grade == "high"
