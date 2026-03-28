# Task: Write unit tests for the deterministic rules engine

Write pytest tests for the three new services: `pension_calculator.py`, `eligibility.py`, and `suitability.py`. These are pure computation — no database, no LLM, no async. Tests should be fast and deterministic.

Read `CLAUDE.md` for project context. Read the three service files before writing tests.

## Setup

Create `backend/tests/` directory with:
- `__init__.py`
- `conftest.py` — minimal, just path setup if needed
- `test_pension_calculator.py`
- `test_eligibility.py`
- `test_suitability.py`

## test_pension_calculator.py

Test with known inputs and hand-verified expected outputs:

**ITP1 client, 650k income:**
- Tjänstepension should split at 7.5 × IBB ceiling
- Below ceiling: 4.5%, above ceiling: 30%
- Allmän pension: 16% + 2.5% of PGI (income × 0.93, capped at 8.07 × IBB)

**SAF-LO client, 400k income:**
- All below ceiling → 4.5% flat
- Different provider set than ITP1

**High earner, ITP1, 1.2M income:**
- Significant portion above ceiling at 30%
- Verify the split is correct

**ITP2 client:**
- Should note it's defined benefit, not compute contribution rates the same way

**Edge cases:**
- Client with no income → should handle gracefully, not crash
- Client with no collective agreement (none) → should still return something useful
- Client with retirement age already passed → handle gracefully
- Income exactly at the ceiling boundary

**Salary exchange:**
- Verify tax savings calculation for income above state tax breakpoint (~613,900 SEK)
- Verify for income below breakpoint (no state tax, lower marginal rate)
- Verify not eligible for self-employed

**IBB values:**
- Verify the IBB lookup returns correct published values for 2024, 2025, 2026

## test_eligibility.py

**Agreement → provider mapping:**
- ITP1 → should include Collectum, Alecta, AMF, SPP, etc.
- SAF-LO → should include Fora, AMF, Folksam, etc.
- PA16 → should include SPV, Kåpan

**Recommendation type eligibility:**
- salary_exchange + employed + ITP1 → eligible
- salary_exchange + self_employed → not eligible
- salary_exchange + retired → not eligible
- decumulation + retired → eligible
- decumulation + employed age 30 → not eligible or warning
- transfer_advice → generally eligible for most agreements
- survivor_protection → always eligible

**Edge cases:**
- Unknown collective agreement → graceful handling
- Missing employment status → graceful handling

## test_suitability.py

**Full data client:**
- All fields filled → data completeness factor should be high (close to 1.0)
- Score should be reasonable (0.6+)

**Minimal data client (only required fields):**
- Missing income, risk_profile, retirement_age → data completeness low
- Overall score should be lower

**Risk profile matching:**
- If scenarios exist with risk indicators, test that matching produces higher score
- No scenarios → risk factor defaults to 0.5

**Agreement eligibility factor:**
- salary_exchange + ITP1 + employed → eligibility factor high
- salary_exchange + none agreement → eligibility factor low

**Age appropriateness:**
- salary_exchange for 63-year-old with retirement at 65 → low age score (too late)
- pension_review for 45-year-old with retirement at 65 → high age score (20 years out)

**Score grade boundaries:**
- Score ≥ 0.7 → "high"
- Score 0.4–0.7 → "moderate"
- Score < 0.4 → "low"
- Test values near the boundaries

## Running

After writing, run:
```bash
cd backend && source .venv/bin/activate && pytest tests/ -v
```

All tests must pass. If any fail, fix the test or the service (if the service has a bug).

## Constraints

- No mocking needed — these are pure functions
- No database fixtures needed
- No async — all sync tests
- Use `pytest.approx()` for float comparisons
- Each test function should test one specific thing with a clear name like `test_itp1_below_ceiling_contribution_rate`
- Add brief docstrings explaining what each test verifies and the expected math
