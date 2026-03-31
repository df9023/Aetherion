# Task: Build Firm Memory Phase 1 — Advisor Insights

Read `CLAUDE.md` for project context. Read existing models, schemas, endpoints, and frontend components to match patterns.

## Concept

Firm Memory captures institutional knowledge that lives in advisors' heads — things like "McKinsey HR requires 3-month notice before salary exchange" or "for manufacturing clients, double-check overtime doesn't dip them below the ceiling." This is knowledge specific to *this firm*, distinct from the regulatory knowledge base.

Phase 1 is simple and requires no ML: advisors create structured notes (we call them "insights") that are tagged, stored, and **surfaced automatically in future relevant cases**.

---

## 1. Backend — new model

Create `backend/app/models/firm_insight.py`:

```python
class FirmInsight(Base):
    __tablename__ = "firm_insights"

    id: UUID PK
    organization_id: UUID FK → organizations.id
    created_by: UUID FK → users.id

    # Content
    title: str (max 255)
    content: str (Text) — the actual insight
    category: FirmInsightCategory enum

    # Scoping — what this insight applies to (all optional, multiple can be set)
    case_types: list[str] (ARRAY) — e.g. ["salary_exchange", "pension_review"]
    collective_agreements: list[str] (ARRAY) — e.g. ["ITP1", "SAF_LO"]
    client_organization_id: UUID FK → client_organizations.id (nullable) — specific employer
    tags: list[str] (ARRAY) — free-form tags for search

    # Metadata
    source_case_id: UUID FK → cases.id (nullable) — the case this insight came from
    is_active: bool (default true)
    upvotes: int (default 0) — other advisors can endorse
    created_at: datetime
    updated_at: datetime
```

Add a new enum `FirmInsightCategory` to `backend/app/models/base.py`:

```python
class FirmInsightCategory(str, enum.Enum):
    CLIENT_SPECIFIC = "client_specific"      # About a specific employer/client org
    PRODUCT_TIP = "product_tip"              # Provider/product quirks
    PROCESS_NOTE = "process_note"            # How to handle a specific workflow
    COMPLIANCE_TIP = "compliance_tip"        # Compliance edge cases
    LESSON_LEARNED = "lesson_learned"        # Post-case reflections
    GENERAL = "general"
```

Register in `models/__init__.py`.

## 2. Backend — schemas

Create `backend/app/schemas/firm_insight.py`:

- `FirmInsightCreate` — title, content, category, case_types, collective_agreements, client_organization_id, tags, source_case_id
- `FirmInsightUpdate` — all optional
- `FirmInsightResponse` — all fields + id, org_id, created_by, creator_name (from relationship), created_at, updated_at

Register in `schemas/__init__.py`.

## 3. Backend — endpoints

Create `backend/app/api/v1/endpoints/firm_insights.py`:

- `POST /` — create insight (org-scoped)
- `GET /` — list insights for the org, with optional filters:
  - `?case_type=salary_exchange` — filter by case type
  - `?collective_agreement=ITP1` — filter by agreement
  - `?client_organization_id=uuid` — filter by employer
  - `?category=product_tip` — filter by category
  - `?search=keyword` — text search in title + content
- `GET /{id}` — get single insight
- `PATCH /{id}` — update insight
- `DELETE /{id}` — delete (only creator or admin)
- `POST /{id}/upvote` — increment upvote counter (one per user — track in a simple way)

**Key endpoint — contextual matching:**

- `GET /relevant?case_id=uuid` — given a case, return insights that match its context. Match logic:
  - Match on `case_types` containing the case's `case_type`
  - Match on `collective_agreements` containing the client's `collective_agreement`
  - Match on `client_organization_id` matching the client's `client_organization_id`
  - Order by: specificity (more matching fields = higher rank), then upvotes, then recency
  - Limit to 10

Register as `/api/v1/firm-insights` in the router.

## 4. Backend — Alembic migration

Create migration for the `firm_insights` table. Add the `FirmInsightCategory` enum type.

## 5. Frontend — hooks

Add to `frontend/lib/hooks.ts`:

```typescript
export interface FirmInsightResponse {
  id: string
  organization_id: string
  title: string
  content: string
  category: string
  case_types: string[]
  collective_agreements: string[]
  client_organization_id: string | null
  tags: string[]
  source_case_id: string | null
  is_active: boolean
  upvotes: number
  created_by: string
  created_at: string
  updated_at: string
}

export function useFirmInsights(filters?: Record<string, string>) { ... }
export function useRelevantInsights(caseId: string) { ... }
export function useCreateFirmInsight() { ... }
export function useUpvoteFirmInsight() { ... }
```

## 6. Frontend — Firm Insights panel on case detail page

Add a new card component `frontend/components/firm-insights-card.tsx` that appears on the case detail page (right sidebar, below or near the knowledge base card).

**Header:** "Firmans insikter" with a lightbulb icon and count badge

**When insights exist for this case:**
Show each relevant insight as a compact card:
- Category badge (color-coded)
- Title (bold)
- Content (2-3 lines, expandable)
- Author name + date
- Upvote button with count
- If linked to a client org: show org name
- If linked to a source case: "Från ärende: [case title]" link

**Empty state:** "Inga insikter matchar detta ärende ännu"

**"Lägg till insikt" button** — opens a dialog where the advisor can:
- Write a title and content
- Select category from dropdown (Swedish labels)
- Pre-filled with the current case's type and client's collective agreement as scope
- Pre-filled source_case_id with current case
- Optional: tag the client organization
- Optional: add free-form tags

## 7. Frontend — Firm Insights standalone page

Create `frontend/app/(dashboard)/insights/page.tsx` — a browseable list of all firm insights.

- Header: "Firmans kunskapsbank" with "Ny insikt" button
- Filter bar: category dropdown, case type dropdown, collective agreement dropdown
- Search input
- Card grid of insights (similar to knowledge page layout)
- Each card: title, content preview, category badge, tags, upvotes, author, date
- Clickable → expand full content (inline or modal)

Add "Insikter" to the sidebar in `frontend/components/sidebar.tsx` using the `Lightbulb` icon from lucide-react. Place it after "Kunskapsbas".

## 8. Frontend — Post-case insight prompt

After a case status changes to `completed`, show a subtle prompt at the top of the case detail page:

> "Har du lärdomar från detta ärende? [Lägg till insikt]"

This encourages advisors to capture knowledge while it's fresh. The button opens the same create dialog, pre-filled with the case context.

## Important

- All UI text in Swedish
- Match existing design system
- Multi-tenant: insights are org-scoped, never leak across orgs
- The `GET /relevant` endpoint is the core value — it must correctly match insights to cases by case_type, agreement, and client org
- Audit entries not strictly required for insights (they're not compliance-critical), but log creation in the audit trail with a new `INSIGHT_CREATED` action
- Run `pytest backend/tests/ -v --tb=short` after changes
- Add tests in `backend/tests/test_firm_insights.py`:
  - CRUD tests (create, list, get, update, delete)
  - Relevance matching (create insights with different scopes, verify correct ones returned for a case)
  - Org isolation
  - Upvote
  - Delete only by creator or admin
