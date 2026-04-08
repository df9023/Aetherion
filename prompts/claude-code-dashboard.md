# Task: Build the Advisor Dashboard

Create a dashboard page at `/dashboard` that serves as the advisor's home screen — the first thing they see after logging in. It should feel like a command center: what needs my attention, what's coming up, and how am I doing.

Read `CLAUDE.md` for project context. Read the existing pages and components to match the design system exactly.

## Design principles

- **Swedish language** throughout (all labels, headings, empty states)
- **Match existing design system** — same card style (`rounded-xl border border-slate-200/60 bg-white shadow-sm`), same spacing, same font sizes (minimum `text-xs`, prefer `text-sm` for body)
- **No `text-[10px]` or `text-[11px]`** anywhere
- **Information hierarchy** — most important/actionable items at the top
- **Clean whitespace** — don't cram everything together
- **Real data** from existing API endpoints via React Query hooks in `frontend/lib/hooks.ts`

## Route setup

1. Create `frontend/app/(dashboard)/dashboard/page.tsx`
2. Update `frontend/app/page.tsx` to redirect to `/dashboard` instead of `/cases`
3. Add "Översikt" (Overview) as the first nav item in `frontend/components/sidebar.tsx` using the `LayoutDashboard` icon from lucide-react — it should appear above "Ärenden"

## Dashboard sections (top to bottom)

### 1. Greeting header
- "God morgon, Erik" (or appropriate Swedish greeting based on time of day: morgon < 12, eftermiddag 12-17, kväll > 17)
- Subtitle: today's date formatted in Swedish (`"onsdag 18 mars 2026"`)
- Right side: quick action buttons — "Nytt ärende" and "Ny klient" (open the existing create dialogs)

### 2. Key metrics row (4 cards in a grid)
Pull from the cases and clients data you already have:

| Metric | Label | Source |
|--------|-------|--------|
| Active cases | Aktiva ärenden | `cases.filter(c => c.status !== 'archived' && c.status !== 'completed').length` |
| Awaiting review | Väntar granskning | `cases.filter(c => c.status === 'ready_for_review' || c.status === 'in_review').length` |
| Meetings this week | Möten denna vecka | `cases.filter(c => c.meeting_date && isThisWeek(c.meeting_date)).length` |
| Completed this month | Avslutade denna månad | `cases.filter(c => c.status === 'completed' && isThisMonth(c.completed_at)).length` |

Each card: large number, label below, subtle icon, colored left border or background accent.

### 3. Two-column layout below metrics

**Left column (wider, ~60%):**

#### 3a. Cases needing attention ("Kräver åtgärd")
Show cases that need the advisor's action, ordered by urgency:
1. `ready_for_review` status cases (amber highlight — need review)
2. `draft` status cases (gray — need to be started)
3. Cases with `meeting_date` in the next 3 days that don't have a recommendation yet

Each row: case title, client name (from clients list), status badge (Swedish), time since last update. Clickable → navigates to case detail. Limit to 5, with "Visa alla ärenden →" link to `/cases`.

If no cases need attention: friendly empty state "Alla ärenden är uppdaterade" with a checkmark icon.

#### 3b. Recent activity ("Senaste aktivitet")
Pull from audit trail entries across all cases. Show the last 8 actions.
Each entry: icon (AI/user), action description (Swedish from `auditActionLabels`), case title, relative time.
Clickable → navigates to the case.

You'll need a new API hook since the current audit hook is per-case. Create a new backend endpoint:
- `GET /api/v1/audit/recent?limit=10` — returns the most recent audit entries across all cases for the org
- Add this to `frontend/lib/hooks.ts` as `useRecentAudit()`

**Right column (~40%):**

#### 3c. Upcoming meetings ("Kommande möten")
Cases with `meeting_date` in the future, sorted by date ascending. Show next 5.
Each row: date (Swedish format), client name, case title, meeting prep status (brief generated or not — show a green checkmark or amber "Ej förberett").
Clickable → navigates to case detail.

If no upcoming meetings: "Inga planerade möten" with calendar icon.

#### 3d. Quick stats / performance ("Din månad")
Simple summary card:
- Rekommendationer genererade: count of `recommendation_generated` audit actions this month
- Dokument skapade: count of `document_generated` audit actions this month  
- Ärenden avslutade: count of completed cases this month

Show as a clean list with numbers, no charts needed.

## Backend endpoint to add

### `GET /api/v1/audit/recent`

Add to `backend/app/api/v1/endpoints/` (either in the existing audit/cases file or a new `dashboard.py`):

```python
@router.get("/audit/recent", response_model=list[AuditEntryResponse])
async def get_recent_audit(
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get most recent audit entries across all cases for the org."""
    result = await db.execute(
        select(AuditEntry)
        .join(Case, AuditEntry.case_id == Case.id)
        .where(Case.organization_id == current_user.organization_id)
        .order_by(AuditEntry.timestamp.desc())
        .limit(limit)
    )
    return result.scalars().all()
```

Wire it into the API router and add the frontend hook.

## Important

- Use the existing `useCases()`, `useClients()` hooks for data — don't create new ones for data you already have
- Use the existing `CreateCaseDialog` and `CreateClientDialog` components for the quick action buttons
- Import label maps from `frontend/lib/labels.ts` — all status/type/audit labels are already Swedish
- Don't build features that require endpoints that don't exist (except the audit/recent one specified above)
- The dashboard should load fast — it's fetching data that's already cached by React Query from sidebar badge counts
- Handle loading state with skeletons matching the layout
- Handle empty states gracefully with Swedish text and appropriate icons
