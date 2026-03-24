# Visual Redesign — Match Frontend to v0 Reference

## Goal

Update the existing `frontend/` to match the visual design in `v0-reference/`. The v0 reference is a static prototype with mock data. Our existing frontend has a working data layer (React Query hooks, API client, providers, mutations). **Keep all data wiring intact. Only change the visual/styling layer.**

## Critical Rules

1. **DO NOT touch** `frontend/lib/api.ts`, `frontend/lib/hooks.ts`, or `frontend/components/providers.tsx` — these are the data layer and must stay as-is.
2. **DO NOT replace** React Query hooks with mock data. Every page currently uses `useQuery`/`useMutation` hooks — keep them.
3. **DO NOT delete** any existing component files. Restyle them in place.
4. **DO copy** visual patterns, class names, and layout structures from the v0 reference components.
5. The v0 reference uses `(app)` as the route group. Our existing frontend uses `(dashboard)`. Keep `(dashboard)`.
6. If the v0 reference has a component that doesn't exist in our frontend, create it but wire it to real data (not mock).

## File-by-File Instructions

### 1. `frontend/app/globals.css`

Replace the CSS variables and theme with the v0 reference version from `v0-reference/app/globals.css`. Keep our existing `@keyframes fadeIn` block and the `--font-sans: var(--font-inter)` definition. The v0 reference has cleaner variable definitions — use those.

### 2. `frontend/components/sidebar.tsx`

Replace the entire component with the v0 reference version from `v0-reference/components/sidebar.tsx`. It has:
- `bg-slate-950` dark sidebar
- Gradient logo mark (sky-400 → blue-600) with "Aetherion" text
- "Workspace" section label
- Nav items with count badges (`bg-slate-800 text-slate-400`)
- Active state: `border-l-2 border-sky-400 bg-sky-500/10 text-sky-400`
- User area at bottom with initials avatar, name, role, settings gear

**Additions to make** (not in v0 reference but needed):
- The nav badge counts should be dynamic. If you can easily wire them to query data (e.g., `useCases()?.length`), do it. Otherwise, keep them static for now.

### 3. `frontend/components/top-bar.tsx`

Replace with the v0 reference `Topbar` from `v0-reference/components/topbar.tsx`. It has:
- Sticky top bar with `bg-white/80 backdrop-blur-sm`
- Breadcrumbs via props (keep the existing breadcrumb logic that dynamically fetches case/client names)
- Centered fake search bar with `⌘K` kbd badge
- Right side: notification bell with red dot, user initials avatar, "SPP" org badge

**Important**: Our current `top-bar.tsx` has dynamic breadcrumb logic that uses `useCase()` and `useClient()` hooks to show real titles. Keep that logic, but apply the v0 visual style. The v0 reference takes breadcrumbs as a prop — adapt accordingly. The pages should pass breadcrumbs to the top bar.

### 4. `frontend/app/(dashboard)/layout.tsx`

Update the layout structure to match `v0-reference/app/(app)/layout.tsx`:
```
<div className="min-h-screen bg-slate-50">
  <Sidebar />
  <div className="ml-64 flex min-h-screen flex-col">
    {children}
  </div>
</div>
```
Keep the `<Providers>` wrapper and `<Toaster />` that already exist in our layout.

### 5. `frontend/app/(dashboard)/cases/page.tsx` — Cases Dashboard

Restyle to match `v0-reference/app/(app)/cases/page.tsx`. Key visual changes:
- Add stats bar at top (4 metric cards in a grid). Compute numbers from the `cases` data: count by status, unique clients, etc.
- Filter pills (status + type) with `bg-sky-500 text-white` active state, `bg-slate-100 text-slate-600` inactive
- Vertical divider `|` between status and type pill groups
- Case cards with:
  - 3px progress bar at top (colored by status)
  - Client initials avatar (slate-100 circle)
  - Title that turns `text-sky-600` on hover
  - Status badge + type badge
  - Footer with advisor name + timestamp separated by `border-t border-slate-100`
  - Hover: `border-l-4 border-l-sky-400` slides in
- Empty state: `Inbox` icon centered with message and button

**Keep**: `useCases()` hook, loading skeletons, `CreateCaseDialog` integration, router navigation on card click.

### 6. `frontend/app/(dashboard)/cases/[id]/page.tsx` — Case Detail

Restyle to match `v0-reference/app/(app)/cases/[id]/page.tsx`. Key changes:
- Two-column layout: main `flex-1` + right panel `w-[380px]`
- Page passes breadcrumbs to `Topbar`
- Left column: `CaseHeaderCard` → `MeetingPrepCard` → `ClientInfoCard` → `AIRecommendationCard` (vertical stack with `gap-5`)
- Right column: `KnowledgeBaseCard` → `AuditTrailCard`

**Keep all existing data wiring**: `useCase()`, `useClient()`, `useCaseRecommendations()`, `useRecommendationEvidence()`, `useCaseAudit()`, `useKnowledgeSearch()`, `useGenerateMeetingBrief()`, `generateRec.mutate()`, `generateDoc.mutate()`, `downloadDocument()`.

Break the case detail page into sub-components following the v0 pattern. Each card component should accept data as props (fetched by the page). Reference:
- `v0-reference/components/case-header-card.tsx`
- `v0-reference/components/meeting-prep-card.tsx`
- `v0-reference/components/client-info-card.tsx`
- `v0-reference/components/ai-recommendation-card.tsx`
- `v0-reference/components/knowledge-base-card.tsx`
- `v0-reference/components/audit-trail-card.tsx`

For `meeting-prep-card`: Use the v0 visual design (pillar cards with colored borders, severity badges, scenario grid, talking points, agenda timeline) but wire it to real data from `useGenerateMeetingBrief()`. Our existing `frontend/components/meeting-brief-viewer.tsx` has the data wiring — merge the v0 visual design into it.

For `ai-recommendation-card`: Use the v0 visual design (suitability score bar, reasoning chain timeline, evidence cards, action buttons) but keep the real data from `useCaseRecommendations()` and `useRecommendationEvidence()`.

### 7. `frontend/app/(dashboard)/clients/page.tsx` — Clients List

Restyle to match `v0-reference/app/(app)/clients/page.tsx`:
- Page header with "Clients" + "New Client" button
- Search with `Search` icon
- Client cards in a 3-column grid
- Each card: initials avatar, name, age, employer with `Building2` icon, monthly income, risk badge with `Shield` icon
- Hover: `border-l-4 border-l-sky-400`
- Empty state: `Users` icon centered

**Keep**: `useClients()` hook, `CreateClientDialog` integration, loading skeletons, router links to `/clients/[id]`.

### 8. `frontend/app/(dashboard)/clients/[id]/page.tsx` — Client Detail

Restyle to match `v0-reference/app/(app)/clients/[id]/page.tsx`:
- Two-column layout: `lg:grid-cols-3`, left side `lg:col-span-2`
- Left: `ClientHeaderCard` → `ClientDetailsCard` → `DocumentIngestionCard`
- Right: `LinkedCasesCard`

Reference:
- `v0-reference/components/client-header-card.tsx`
- `v0-reference/components/client-details-card.tsx`
- `v0-reference/components/document-ingestion-card.tsx`
- `v0-reference/components/linked-cases-card.tsx`

For `DocumentIngestionCard`: Use the v0 visual design (upload dropzone, extraction progress steps, review grid with confidence indicators and diff arrows, fund allocations table) but keep the real data wiring from our existing `frontend/components/document-ingestion.tsx` (`useIngestDocument()`, `useApplyExtraction()`).

**Keep**: `useClient()`, `useClientCases()`, `CreateCaseDialog` integration.

### 9. `frontend/app/(dashboard)/knowledge/page.tsx` — Knowledge Base

Restyle to match `v0-reference/app/(app)/knowledge/page.tsx`:
- Centered layout (`max-w-4xl`)
- Search with `Search` icon
- Category filter pills
- Knowledge items with: title, category badge, source, tags, expandable content with "Show more"/"Show less"
- Hover: `border-l-4 border-l-sky-400`
- Chevron icons for expand/collapse
- Empty state: `BookOpen` icon

**Keep**: `useKnowledge()` hook, loading skeletons.

### 10. `frontend/components/create-case-dialog.tsx`

Restyle to match `v0-reference/components/create-case-dialog.tsx`. Keep all the existing form logic, `useCreateCase()` mutation, client selector from API, and redirect-on-success behavior. Just update the visual styling.

### 11. `frontend/components/create-client-dialog.tsx`

Restyle to match `v0-reference/components/create-client-dialog.tsx`. Keep all the existing form logic, `useCreateClient()` mutation, and validation. Just update the visual styling.

## General Pattern

For every page/component, follow this approach:
1. Read the v0 reference component for the visual structure and Tailwind classes
2. Read the existing frontend component for the data wiring
3. Merge: keep all hooks, mutations, API calls, loading states, and error handling from the existing code, but apply the visual layout, classes, and structure from the v0 reference

## shadcn/ui Components

If the v0 reference uses shadcn/ui components that aren't installed yet in our frontend, install them:
```bash
cd frontend && npx shadcn@latest add [component-name]
```

Check what's already installed in `frontend/components/ui/` before installing.

## Verification

After all changes, verify:
1. `cd frontend && npm run build` — zero build errors
2. All pages render correctly with real data from the backend (not mock data)
3. All mutations work: create case, create client, generate recommendation, generate meeting brief, upload document, generate document, download document
4. Loading states show skeletons
5. Empty states show the correct messaging
6. Navigation between pages works correctly
7. Breadcrumbs show real case/client names
