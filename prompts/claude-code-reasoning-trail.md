# Task: Upgrade Reasoning Trail to first-class compliance record

Read `CLAUDE.md` for project context. Read the existing recommendation model, schemas, endpoints, reasoner service, document service, and the AI recommendation frontend component to understand what exists.

## Context

The recommendation system already produces a `reasoning_chain` (list of steps with descriptions, evidence IDs, and conclusions) stored as JSONB on the Recommendation model. The goal is to upgrade this from a display-only feature into a **first-class auditable compliance record** that advisors can annotate and that drives document generation.

Three changes:
1. **Advisor annotations** on individual reasoning steps
2. **Reasoning chain as structured compliance record** with metadata
3. **Document generation uses the chain** as its source of truth

---

## 1. Backend — Reasoning Trail model upgrade

### Update the ReasoningStep schema

In `backend/app/schemas/recommendation.py`, expand `ReasoningStep`:

```python
class ReasoningStep(BaseModel):
    step: int
    title: str  # NEW — short label e.g. "Klientsituation", "Behovsanalys", "Lämplighetsbedömning"
    description: str
    evidence_ids: list[UUID] = []
    conclusion: str
    cited_texts: list[str] = []  # NEW — verbatim quotes used in this step (from Citations API)
    advisor_annotation: Optional[str] = None  # NEW — human note added by advisor
    annotated_by: Optional[UUID] = None  # NEW — who annotated
    annotated_at: Optional[datetime] = None  # NEW — when annotated
```

### Add reasoning metadata to Recommendation

In `backend/app/models/recommendation.py`, add a new JSONB column:

```python
reasoning_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
```

This stores:
```json
{
  "total_steps": 5,
  "annotated_steps": 2,
  "annotation_complete": false,
  "reviewed_by": null,
  "reviewed_at": null,
  "compliance_status": "pending_review"
}
```

### Create Alembic migration

Add the `reasoning_metadata` column to the `recommendations` table. The `reasoning_chain` JSONB column already exists and will store the expanded step structure — no schema change needed for it (JSONB is flexible).

---

## 2. Backend — Annotation endpoint

Add to `backend/app/api/v1/endpoints/recommendations.py`:

### `PATCH /api/v1/recommendations/{id}/reasoning/{step_number}/annotate`

```python
class AnnotateStepRequest(BaseModel):
    annotation: str  # The advisor's note

@router.patch("/{recommendation_id}/reasoning/{step_number}/annotate")
async def annotate_reasoning_step(
    recommendation_id: UUID,
    step_number: int,
    body: AnnotateStepRequest,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> RecommendationResponse:
    """Add an advisor annotation to a specific reasoning step."""
    # Load recommendation (verify org)
    # Find the step by step_number in reasoning_chain
    # Set advisor_annotation, annotated_by, annotated_at
    # Update reasoning_metadata.annotated_steps count
    # Create audit entry: RECOMMENDATION_EDITED with details {"action": "step_annotated", "step": step_number}
    # Save and return
```

### `POST /api/v1/recommendations/{id}/reasoning/review`

```python
@router.post("/{recommendation_id}/reasoning/review")
async def mark_reasoning_reviewed(
    recommendation_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> RecommendationResponse:
    """Mark the reasoning chain as reviewed by the advisor (compliance sign-off)."""
    # Set reasoning_metadata.reviewed_by, reviewed_at, compliance_status = "reviewed"
    # Create audit entry: RECOMMENDATION_REVIEWED with details {"action": "reasoning_reviewed"}
    # Return updated recommendation
```

---

## 3. Backend — Update reasoner to populate step titles

In `backend/app/services/reasoner.py`, when building the reasoning chain from the Citations API response (Pass 2), assign structured `title` values to each step. Map the reasoning steps to standard IDD suitability assessment phases:

```python
STEP_TITLES = [
    "Klientsituation",           # Client situation analysis
    "Behovsanalys",              # Needs identification
    "Alternativbedömning",       # Option evaluation
    "Lämplighetsbedömning",      # Suitability assessment
    "Produktmatchning",          # Product matching
    "Kostnadsinformation",       # Cost disclosure (IDD)
    "Intressekonfliktbedömning", # Conflict of interest
]
```

When creating each reasoning step, try to match the content to one of these titles. If the LLM produces fewer or more steps, use what's available. Also populate `cited_texts` for each step from the citations API response — extract the verbatim quotes that belong to that step.

Also initialize `reasoning_metadata`:
```python
reasoning_metadata = {
    "total_steps": len(chain),
    "annotated_steps": 0,
    "annotation_complete": False,
    "reviewed_by": None,
    "reviewed_at": None,
    "compliance_status": "generated",
}
```

---

## 4. Backend — Update document generation

In `backend/app/services/document.py`, update the recommendation pack generation to use the reasoning chain as the source of truth for the suitability assessment sections.

Currently, the document service pulls `summary`, `assumptions`, `scenarios` etc. as separate fields. Add a section that renders the full reasoning chain:

For each reasoning step:
- Render the **title** as a subheading (e.g. "4.1 Lämplighetsbedömning")
- Render the **description** as the body text
- Render any **cited_texts** as indented blockquotes
- Render the **advisor_annotation** (if present) in a highlighted box labeled "Rådgivarens kommentar:"
- Render the **conclusion** as a summary line

This means the document is generated *from* the reasoning chain — the chain IS the compliance documentation, not a separate artifact.

---

## 5. Frontend — Reasoning Trail UI

Update `frontend/components/ai-recommendation-card.tsx` to show the enhanced reasoning trail.

### Reasoning chain display

Replace the current simple step list with an expandable, annotatable trail:

Each step renders as a card:
```
┌─────────────────────────────────────────────┐
│ Steg 3 — Alternativbedömning               │
│                                             │
│ [description text...]                       │
│                                             │
│ ┌─ Citat ─────────────────────────────────┐ │
│ │ "Lönväxling innebär att..."             │ │
│ │ — FFFS 2018:10, §4                      │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ Slutsats: [conclusion text]                 │
│                                             │
│ ┌─ Rådgivarens kommentar ─────────────────┐ │
│ │ "Diskuterat med Anna, hon bekräftar..." │ │
│ │ — Erik Eriksson, 2026-03-18             │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ [Lägg till kommentar]  (if no annotation)   │
└─────────────────────────────────────────────┘
```

- Steps are expanded by default (the chain IS the content, not hidden away)
- Each step shows: step number + title, description, cited texts as blockquotes, conclusion, and annotation (if any)
- "Lägg till kommentar" button opens an inline textarea for the advisor to type their note
- Existing annotations show the advisor name and date
- A "Markera som granskad" button at the bottom of the chain (calls the review endpoint)
- After review: show a green badge "Granskad av Erik Eriksson, 2026-03-18"

### Frontend hooks

Add to `frontend/lib/hooks.ts`:

```typescript
export function useAnnotateStep(recommendationId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: { step_number: number; annotation: string }) =>
      apiFetch(`/recommendations/${recommendationId}/reasoning/${data.step_number}/annotate`, {
        method: "PATCH",
        body: JSON.stringify({ annotation: data.annotation }),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["recommendation"] })
    },
  })
}

export function useReviewReasoning(recommendationId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () =>
      apiFetch(`/recommendations/${recommendationId}/reasoning/review`, {
        method: "POST",
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["recommendation"] })
    },
  })
}
```

### Update RecommendationResponse type

Add to the frontend type:
```typescript
export interface ReasoningStep {
  step: number
  title: string
  description: string
  evidence_ids: string[]
  conclusion: string
  cited_texts: string[]
  advisor_annotation: string | null
  annotated_by: string | null
  annotated_at: string | null
}

export interface ReasoningMetadata {
  total_steps: number
  annotated_steps: number
  annotation_complete: boolean
  reviewed_by: string | null
  reviewed_at: string | null
  compliance_status: string
}
```

Add `reasoning_metadata: ReasoningMetadata | null` to `RecommendationResponse`.

---

## 6. Frontend — Compliance status badge

Show the reasoning trail's compliance status on the case header and in the cases list:

- `"generated"` → gray badge "AI-genererad"
- `"pending_review"` → amber badge "Väntar granskning"
- `"reviewed"` → green badge "Granskad"

This is a small visual indicator next to the recommendation status.

---

## Important

- All UI text in Swedish
- Match existing design system (card styles, spacing, colors, font sizes)
- Backward compatible — existing recommendations without the new fields should still render (check for null/undefined)
- The annotation feature must create audit entries (every annotation is logged)
- Run `pytest backend/tests/ -v --tb=short` to verify nothing breaks
- Add tests in `backend/tests/test_reasoning_trail.py`:
  - `test_annotate_step` — annotating a step updates the chain and metadata
  - `test_annotate_step_not_found` — invalid step number returns 404
  - `test_review_reasoning` — marks chain as reviewed
  - `test_org_isolation_annotation` — org2 can't annotate org1's recommendation
