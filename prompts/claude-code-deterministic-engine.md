# Task: Build Deterministic Rules Engine

The core principle: **LLM should only generate narrative text. Everything that can be computed — scores, costs, rates, eligibility — must be calculated in code.** The LLM receives computed facts and explains them, it does not invent numbers.

Read `CLAUDE.md` for full project context before starting.

## What to build

Create three new service files in `backend/app/services/`:

### 1. `suitability.py` — SuitabilityEngine

Replaces the LLM-generated `suitability_score` with a deterministic weighted scoring system.

```python
class SuitabilityEngine:
    def score(self, client: dict, recommendation_type: str, scenarios: list[dict] | None) -> SuitabilityResult
```

`SuitabilityResult` should be a Pydantic model containing:
- `total_score: float` (0.0–1.0)
- `factors: list[SuitabilityFactor]` — each factor with `name`, `score` (0-1), `weight`, `reason` (short explanation)
- `grade: str` — "high" / "moderate" / "low"

**Factors to score** (each 0.0–1.0, multiply by weight, sum and normalize):

| Factor | Weight | Logic |
|--------|--------|-------|
| Risk profile match | 0.25 | If client has `risk_profile` and recommendation includes scenarios: compare scenario risk levels to profile. Full score if aligned, partial if moderate mismatch, low if aggressive rec for low-risk client or vice versa. If no risk profile set, score 0.5 (unknown). |
| Age appropriateness | 0.20 | Score based on years to desired retirement age. If `desired_retirement_age` exists, check if recommendation type makes sense (e.g. salary exchange with 2 years to retirement → low score). If no retirement age, score 0.5. |
| Income adequacy | 0.15 | If `annual_income` exists and recommendation involves costs/contributions, check affordability. If no income data, score 0.5. |
| Agreement eligibility | 0.20 | Check if the `collective_agreement` is compatible with the `recommendation_type`. E.g., salary exchange only makes sense for employed people with ITP1/ITP2/SAF_LO. Score 1.0 if eligible, 0.3 if unclear, 0.0 if ineligible. |
| Data completeness | 0.20 | Score based on how many client fields are filled: name, dob, employer, agreement, income, risk_profile, retirement_age. Each filled field adds to score proportionally. |

### 2. `pension_calculator.py` — PensionCalculator

Deterministic Swedish pension math. All numbers must be verifiable against published sources.

```python
class PensionCalculator:
    def calculate(self, client: dict) -> PensionEstimate
```

`PensionEstimate` should be a Pydantic model containing:
- `ibb: int` — current inkomstbasbelopp
- `yearly_contribution: dict` — breakdown by pillar (allman, tjanste, privat)
- `contribution_rates: dict` — the rates used, for transparency
- `projected_monthly_pension: int | None` — rough estimate if enough data
- `salary_exchange_potential: dict | None` — tax savings estimate if applicable
- `notes: list[str]` — caveats and limitations

**Key data to encode:**

IBB (inkomstbasbelopp):
- 2024: 76,200 SEK
- 2025: 80,600 SEK
- 2026: 83,600 SEK

Allmän pension:
- Inkomstpension: 16% of pensionsgrundande inkomst (PGI) up to 8.07 × IBB
- Premiepension: 2.5% of PGI up to 8.07 × IBB
- PGI ≈ annual income × 0.93 (approximate after grundavdrag)

Tjänstepension contribution rates by agreement:
- ITP1: 4.5% on salary ≤ 7.5 × IBB, 30% on salary above 7.5 × IBB
- ITP2: defined benefit, not contribution-based (note this in output)
- SAF-LO: 4.5% on salary ≤ 7.5 × IBB, 30% on salary above
- KAP-KL: 4.5% on salary ≤ 7.5 × IBB, 30% above (verify)
- AKAP-KL: 4.5% + age-based additional 0-2%
- PA16: avdelning 1 (4.5%/30%), avdelning 2 (defined benefit component)

Salary exchange estimate (if `recommendation_type` is `salary_exchange`):
- Tax savings = exchange_amount × marginal_tax_rate
- Marginal tax rate: ~32% municipal tax + 20% state tax above breakpoint (~613,900 SEK for 2026)
- Net benefit = employer contribution to pension (typically exchange amount × ~1.06 after social fee savings) − lost income after tax

### 3. `eligibility.py` — EligibilityChecker

Lookup tables for what's possible given a client's situation.

```python
class EligibilityChecker:
    def check(self, client: dict, recommendation_type: str) -> EligibilityResult
```

`EligibilityResult`:
- `eligible: bool`
- `reasons: list[str]` — why eligible or not
- `eligible_providers: list[str]` — which providers are relevant for this agreement
- `warnings: list[str]` — things to be aware of

**Lookup data to encode:**

Agreement → eligible providers:
- ITP1: Collectum (valcentral), choices include Alecta (default), AMF, Folksam, Skandia, SPP, Länsförsäkringar, etc.
- ITP2: Alecta (mandatory for defined benefit portion)
- SAF-LO: Fora (valcentral), choices include AMF (default), Folksam, Handelsbanken, Länsförsäkringar, Nordea, SEB, Skandia, Swedbank
- KAP-KL/AKAP-KL: managed via employer selection
- PA16: SPV (statlig), Kåpan

Recommendation type eligibility:
- salary_exchange: requires employed status + ITP1/ITP2/SAF_LO/KAP_KL + income above certain threshold
- transfer_advice: applicable to most agreements but check lock-in periods
- survivor_protection: always relevant, but options differ by agreement
- decumulation: only for retired or near-retirement clients

## Integration with the Reasoner

After building the three services, update `reasoner.py` → `generate_recommendation()`:

1. **Before** calling the LLM, compute:
   ```python
   pension_calc = PensionCalculator()
   pension_estimate = pension_calc.calculate(client_dict)
   
   eligibility = EligibilityChecker()
   eligibility_result = eligibility.check(client_dict, recommendation_type.value)
   ```

2. **Inject computed facts into the prompt context** that gets passed to `recommendation.j2`:
   ```python
   context["computed"] = {
       "pension_estimate": pension_estimate.model_dump(),
       "eligibility": eligibility_result.model_dump(),
   }
   ```

3. **After** Pass 1 returns (with scenarios and assumptions), compute suitability:
   ```python
   suitability = SuitabilityEngine()
   suitability_result = suitability.score(client_dict, recommendation_type.value, parsed.get("scenarios"))
   ```

4. **Use the deterministic score** instead of the LLM's score:
   ```python
   # Replace: suitability_score=parsed.get("suitability_score")
   suitability_score=suitability_result.total_score
   ```

5. **Store the factor breakdown** in the recommendation's reasoning chain or as a separate field.

## Update the prompt template

Update `backend/app/prompts/recommendation.j2` to include the computed facts:

Add a new section before the instructions:

```jinja
{% if context.computed %}
## Beräknade fakta (använd dessa exakta siffror — räkna INTE om dem)

### Pensionsberäkning
{{ context.computed.pension_estimate | tojson(indent=2) }}

### Behörighet
{{ context.computed.eligibility | tojson(indent=2) }}

VIKTIGT: Använd siffrorna ovan i din rekommendation. Hitta INTE PÅ egna siffror för avgifter, bidragssatser eller pensionsbelopp.
{% endif %}
```

Also **remove** `suitability_score` from the `RECOMMENDATION_TOOL` schema in `reasoner.py` — it's now computed in code, not by the LLM.

## Important constraints

- All computed values must be **traceable** — include the source rates/formulas in the output so an advisor can verify
- Handle missing data gracefully — if `annual_income` is None, skip income-dependent calculations and note it
- All monetary values in SEK
- Type hints everywhere, Pydantic models for all inputs/outputs
- Add docstrings explaining the formulas and their sources
- IBB and tax breakpoints should be in a simple dict/config at the top of the file so they're easy to update yearly
- Do NOT create database migrations — these services are pure computation, no new tables needed
- Do NOT modify the frontend — the suitability score is already displayed correctly as a 0-1 value

## Verification

After building, test with:
```bash
cd backend && source .venv/bin/activate
python -c "
from app.services.suitability import SuitabilityEngine, SuitabilityResult
from app.services.pension_calculator import PensionCalculator
from app.services.eligibility import EligibilityChecker

client = {
    'date_of_birth': '1980-05-15',
    'employment_status': 'employed',
    'collective_agreement': 'ITP1',
    'annual_income': '650000',
    'risk_profile': 'moderate',
    'desired_retirement_age': 65,
}

# Pension calculation
pc = PensionCalculator()
est = pc.calculate(client)
print('=== Pension Estimate ===')
print(f'IBB: {est.ibb}')
print(f'Contributions: {est.yearly_contribution}')
print(f'Rates used: {est.contribution_rates}')

# Eligibility
ec = EligibilityChecker()
elig = ec.check(client, 'pension_review')
print(f'\n=== Eligibility ===')
print(f'Eligible: {elig.eligible}')
print(f'Providers: {elig.eligible_providers}')

# Suitability (needs recommendation data)
se = SuitabilityEngine()
result = se.score(client, 'pension_review', None)
print(f'\n=== Suitability ===')
print(f'Score: {result.total_score:.2f} ({result.grade})')
for f in result.factors:
    print(f'  {f.name}: {f.score:.2f} (weight {f.weight})')
"
```

Expected: the pension contribution for ITP1 at 650k income should be roughly 4.5% × 650,000 = 29,250 SEK/year for tjänstepension (since 650k < 7.5 × IBB). The suitability score should be moderate-to-high given all fields are filled.
