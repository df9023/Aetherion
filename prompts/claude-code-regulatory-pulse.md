# Task: Build Regulatory Pulse (Phase 1)

Read `CLAUDE.md` for project context. Read `drident-next-capabilities.md` for the full product vision of Regulatory Pulse. Read existing models, schemas, endpoints, and the dashboard page to match patterns.

## Concept

When a regulation changes (new FI circular, updated collective agreement terms, new tax rules), Regulatory Pulse traces the impact through the firm's active cases and tells advisors exactly what's affected and why.

Phase 1 focuses on: regulatory change tracking, impact matching to active cases, and surfacing impacts in the UI. No automatic updating of recommendations — the advisor always reviews and decides.

---

## 1. Backend — RegulatoryChange model

Create `backend/app/models/regulatory_change.py`:

```python
class RegulatoryChange(Base):
    __tablename__ = "regulatory_changes"

    id: UUID PK
    organization_id: UUID FK → organizations.id
    created_by: UUID FK → users.id

    # What changed
    title: str (max 500) — e.g. "FFFS 2026:4 — Uppdaterade dokumentationskrav för löneväxling"
    description: str (Text) — summary of what changed and why it matters
    source: str (max 255) — e.g. "Finansinspektionen", "Collectum", "Skatteverket"
    source_url: Optional[str] (max 1024) — link to the original publication
    severity: RegulatoryChangeSeverity enum — how urgent this is

    # What it affects (used for matching)
    affected_case_types: list[str] (ARRAY) — e.g. ["salary_exchange", "pension_review"]
    affected_agreements: list[str] (ARRAY) — e.g. ["ITP1", "SAF_LO"]
    affected_tags: list[str] (ARRAY) — free-form tags for broader matching

    # Linked knowledge
    knowledge_item_id: Optional[UUID] FK → knowledge_items.id — the new/updated knowledge item

    # Status tracking
    is_active: bool (default true)
    published_at: datetime — when the regulation was published (external date)
    created_at: datetime
```

Add enum to `backend/app/models/base.py`:

```python
class RegulatoryChangeSeverity(str, enum.Enum):
    CRITICAL = "critical"    # Immediate action required
    HIGH = "high"            # Action needed this week
    MEDIUM = "medium"        # Review when convenient
    LOW = "low"              # Informational
```

## 2. Backend — CaseImpact model

Create `backend/app/models/case_impact.py`:

```python
class CaseImpact(Base):
    __tablename__ = "case_impacts"

    id: UUID PK
    regulatory_change_id: UUID FK → regulatory_changes.id
    case_id: UUID FK → cases.id
    organization_id: UUID FK → organizations.id

    # Why this case is affected
    match_reason: str (Text) — e.g. "Ärendetyp löneväxling med ITP1-avtal matchar ändrade dokumentationskrav"
    affected_sections: list[str] (ARRAY) — which parts of the recommendation need review, e.g. ["suitability_assessment", "cost_disclosure"]

    # Resolution tracking
    status: CaseImpactStatus enum
    resolved_by: Optional[UUID] FK → users.id
    resolved_at: Optional[datetime]
    resolution_note: Optional[str] (Text)

    created_at: datetime
```

Add enum:

```python
class CaseImpactStatus(str, enum.Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    NOT_APPLICABLE = "not_applicable"
```

## 3. Backend — schemas and endpoints

Create schemas for both models (Create, Update, Response). 

Create `backend/app/api/v1/endpoints/regulatory.py`:

**Regulatory Changes:**
- `POST /api/v1/regulatory-changes` — create a new regulatory change (compliance officer or admin)
- `GET /api/v1/regulatory-changes` — list all changes for the org, with filters (?severity=, ?is_active=)
- `GET /api/v1/regulatory-changes/{id}` — get single change with its case impacts

**Impact Management:**
- `POST /api/v1/regulatory-changes/{id}/scan` — **the key endpoint**: scans active cases, creates CaseImpact records for matching cases. Match logic:
  - Case is not archived or completed
  - Case's `case_type` is in `affected_case_types`, OR
  - Client's `collective_agreement` is in `affected_agreements`
  - Generate a `match_reason` explaining why the case matches
  - Skip cases that already have an impact for this change
- `GET /api/v1/regulatory-changes/{id}/impacts` — list all case impacts for a change
- `PATCH /api/v1/case-impacts/{id}/resolve` — mark an impact as resolved with a note
- `PATCH /api/v1/case-impacts/{id}/acknowledge` — mark as acknowledged (advisor saw it)
- `GET /api/v1/cases/{id}/impacts` — list all open impacts for a specific case

Register as `/api/v1/regulatory-changes` and add case impacts routes.

## 4. Backend — Dashboard stats endpoint

Add to the existing dashboard endpoint (or create a new one):

`GET /api/v1/dashboard/compliance-health` — returns:
```json
{
  "total_active_cases": 12,
  "cases_with_open_impacts": 3,
  "total_open_impacts": 5,
  "recent_changes": [{ regulatory change summaries }],
  "impacts_by_severity": { "critical": 1, "high": 2, "medium": 2, "low": 0 }
}
```

## 5. Frontend — hooks

Add to `frontend/lib/hooks.ts`:

- `useRegulatoryChanges()` — list all changes
- `useRegulatoryChange(id)` — single change with impacts
- `useCreateRegulatoryChange()` — create mutation
- `useScanImpacts(changeId)` — trigger scan mutation
- `useResolveImpact()` — resolve mutation
- `useAcknowledgeImpact()` — acknowledge mutation
- `useCaseImpacts(caseId)` — impacts for a specific case
- `useComplianceHealth()` — dashboard stats

## 6. Frontend — Regulatory Pulse page

Create `frontend/app/(dashboard)/regulatory/page.tsx`:

**Header:** "Regulatorisk bevakning" with "Ny regeländring" button

**Compliance health summary cards** at the top:
- Total active cases / cases with open impacts (with percentage)
- Open impacts by severity (color-coded: critical=red, high=amber, medium=blue, low=gray)

**Regulatory changes list** below:
- Each change as a card: severity badge, title, source, published date, impact count ("Påverkar X ärenden")
- Expand to see affected cases list
- "Skanna ärenden" button to run impact scan
- Click into detail view

**Add "Regulatorik" to the sidebar** with `Shield` icon from lucide-react, placed after "Insikter".

## 7. Frontend — Case detail impact banner

In the case detail page (`frontend/app/(dashboard)/cases/[id]/page.tsx`), add an impact banner at the top when the case has open impacts:

```
┌─ ⚠️ Regulatorisk påverkan ──────────────────────────┐
│ 2 regeländringar påverkar detta ärende               │
│                                                       │
│ 🔴 FFFS 2026:4 — Uppdaterade dokumentationskrav     │
│    Påverkar: Lämplighetsbedömning, Kostnadsinformation│
│    [Visa detaljer] [Markera som hanterad]             │
│                                                       │
│ 🟡 Ny IBB 2026 — 85,600 SEK                         │
│    Påverkar: Pensionsberäkningar                      │
│    [Visa detaljer] [Ej tillämpbar]                   │
└───────────────────────────────────────────────────────┘
```

- Severity-colored indicators
- Each impact shows the regulatory change title and affected sections
- "Markera som hanterad" → resolve dialog (requires a note)
- "Ej tillämpbar" → mark as not_applicable
- Banner disappears when all impacts are resolved

## 8. Frontend — Dashboard regulatory card

Add a "Regulatorisk status" card to the dashboard page:
- Shows compliance health: "X av Y ärenden uppdaterade" with a progress bar
- Lists the 3 most recent regulatory changes with impact counts
- "Visa alla →" link to `/regulatory`

## 9. Seed data

Add 2-3 example regulatory changes to the seed script:

1. **"FFFS 2026:4 — Uppdaterade dokumentationskrav för löneväxling"** — severity: high, affects: salary_exchange, ITP1
2. **"IBB 2026 fastställt till 85 600 SEK"** — severity: medium, affects: all case types (pension calculations)
3. **"Collectum: Nya regler för ITP1-val från 2026-07-01"** — severity: medium, affects: pension_review, ITP1

After seeding, auto-run the scan to create example CaseImpact records for existing cases.

## Important

- All UI text in Swedish
- Match existing design system
- Multi-tenant: changes and impacts scoped by organization_id
- The scan endpoint is the core logic — it must correctly match changes to cases via case_type and client's collective_agreement
- Audit entries for: regulatory change created, impact scan completed, impact resolved
- Human-in-the-loop: the system flags, the advisor decides. No automatic recommendation updates.
- Run `pytest backend/tests/ -v --tb=short` after changes
- Add tests in `backend/tests/test_regulatory_pulse.py`:
  - Create regulatory change
  - Scan produces correct impacts (case with matching type gets flagged, non-matching doesn't)
  - Resolve/acknowledge impact
  - Compliance health stats
  - Org isolation
  - Duplicate scan doesn't create duplicate impacts
