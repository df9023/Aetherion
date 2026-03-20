# Claude Code Prompt: Frontend UI Polish

You are working on **Aetherion**, an AI-native decision workspace for Swedish pension advisory. The frontend (Next.js 14 + shadcn/ui + Tailwind) is functionally complete. Your job is to make it look and feel like a polished, professional SaaS product — not a prototype.

## Codebase orientation

Read these files before making changes:
- `frontend/app/(dashboard)/cases/page.tsx` — Cases list page
- `frontend/app/(dashboard)/cases/[id]/page.tsx` — Case detail page
- `frontend/app/(dashboard)/clients/page.tsx` — Clients list page
- `frontend/app/(dashboard)/clients/[id]/page.tsx` — Client detail page
- `frontend/app/(dashboard)/knowledge/page.tsx` — Knowledge base page
- `frontend/app/(dashboard)/layout.tsx` — Dashboard layout (sidebar + topbar + main)
- `frontend/components/sidebar.tsx` — Dark sidebar navigation
- `frontend/components/top-bar.tsx` — Top bar with breadcrumbs
- `frontend/lib/hooks.ts` — All React Query hooks (useCases, useClients, etc.)
- `frontend/lib/labels.ts` — Status/type label and style maps
- `frontend/app/globals.css` — Global styles and CSS variables

Existing design system: dark sidebar (`bg-slate-950`), white cards (`rounded-xl border border-slate-200/60 bg-white shadow-sm`), sky-500 primary, Inter font, Lucide icons.

## Changes to make

### 1. Dashboard stats bar on the Cases page

Above the search/filter row on `/cases`, add a row of 3-4 small metric cards showing:
- Total active cases (count of non-archived cases)
- Cases pending review (count of `ready_for_review` + `in_review` status)
- Total clients (from `useClients()`)
- Cases completed this month (count of `completed` status, optional)

Use the existing cases and clients data from hooks — no new API calls needed. Style as compact stat cards in a horizontal row: small icon, number (large font), label (small muted text). Use a subtle background tint per card (e.g., sky-50, amber-50, emerald-50, slate-50).

### 2. Richer case cards

Update the case cards on `/cases` to include:
- **Client initials avatar** on the left side of each card (small circle with initials, like the client cards already have). You'll need to fetch clients to get the name — use `useClients()` and build a lookup map by ID.
- **Assigned advisor name** shown in the footer metadata area (next to the timestamp). Use the current dev user name or just show "Maria Lindqvist" from the existing data.
- **Workflow progress indicator** — a thin colored bar at the very top of each card (inside the border radius). Color and width based on status:
  - draft: 15% width, slate-300
  - in_preparation: 30% width, blue-400
  - ready_for_review: 50% width, amber-400
  - in_review: 70% width, purple-400
  - approved: 85% width, emerald-400
  - completed: 100% width, green-500
  - archived: 100% width, slate-300

### 3. Sidebar polish

- Replace the small diamond character (`◆`) next to "Aetherion" with a proper SVG icon or a styled div — a rounded square with a gradient (from sky-400 to blue-600) with a subtle inner glow. Make it feel like a real logo mark.
- Add count badges next to nav items showing how many items exist. "Cases" should show the count of active (non-archived) cases. "Clients" shows client count. "Knowledge Base" shows knowledge item count. Use the existing hooks (`useCases`, `useClients`, `useKnowledge`). Style: small rounded pill (`bg-slate-700 text-slate-300 text-[10px] px-1.5 py-0.5`).
- The sidebar needs the hooks to get counts, so the sidebar must become data-aware. Move data fetching into the sidebar component or into the dashboard layout and pass counts as props.

### 4. Top bar enhancement

- Add a **user avatar** (initials circle) on the right side of the top bar, next to the "SPP" badge. Show "EE" for Erik Eriksson with `bg-sky-500/20 text-sky-500`.
- Add a **notification bell icon** (from Lucide: `Bell`) next to the avatar. Just the icon for now, no functionality — but make it look clickable with a hover state. Add a small dot indicator (red, absolute positioned) to suggest unread notifications.
- Add a **global search hint** between the breadcrumbs and the right side: a subtle input-like element showing "Search... ⌘K" that isn't a real input but looks like one (`bg-slate-100 rounded-lg px-3 py-1.5 text-xs text-slate-400`). No functionality needed — it's just visual polish for now.

### 5. Card hover effects

On all list pages (cases, clients, knowledge), improve the card hover states:
- Add a `border-l-4 border-transparent` by default, transitioning to `border-l-4 border-sky-400` on hover. This gives a tactile "selected" feel.
- Ensure the transition is smooth: `transition-all duration-200`.
- Apply consistently across case cards, client cards, and knowledge items.

### 6. Better timestamps with advisor name

On case cards (both on `/cases` list and in the linked cases section on `/clients/[id]`), change the timestamp line from just "Yesterday" to include context:
- Show: "Maria Lindqvist · Yesterday" (or the advisor name if available from data).
- Since we only have user IDs in the case data and no easy user lookup, just hardcode "Maria Lindqvist" for now (she's the advisor in seed data). This is a display-only polish — we'll wire it to real user data later.

### 7. Filter pills instead of select dropdowns

On the Cases page, replace the two `<Select>` dropdowns (status filter and type filter) with horizontally scrollable pill/chip buttons:
- Show all options as small rounded pills in a row.
- Active filter: `bg-sky-500 text-white`. Inactive: `bg-slate-100 text-slate-600 hover:bg-slate-200`.
- "All" is the default active pill for each group.
- Group them: Status pills first, then a subtle vertical divider (`|`), then type pills.
- This is more visual and faster to click than dropdowns.

### 8. Page transition animations

Add subtle fade-in animations when pages load:
- In `frontend/app/globals.css`, add a CSS animation:
  ```css
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
  }
  ```
- Apply `animate-[fadeIn_0.3s_ease-out]` to the main content wrapper of each page (the outermost `<div>` in each page component).

### 9. Keyboard shortcuts

Add basic keyboard shortcuts using a `useEffect` in the dashboard layout:
- `n` — open the "New Case" dialog (requires exposing dialog open state)
- `/` — focus the search input on the current page

For the search shortcut: add a `data-search-input` attribute to search inputs across pages, and in the layout `useEffect`, listen for `/` keypress and focus the element with that attribute.

For the "New Case" shortcut: this is trickier since the dialog state lives in the cases page. A simpler approach: just handle `/` for search focus globally. Skip `n` for now to avoid complexity.

### 10. Empty state illustration

When the cases list has 0 results after filtering (or when a new org has no cases), improve the empty state:
- Instead of just "No cases found" text, show a larger empty state with:
  - A Lucide icon (`Inbox` or `FolderOpen`, sized `h-12 w-12`, in `text-slate-300`)
  - Primary text: "No cases found" (medium weight)
  - Secondary text: "Try adjusting your filters or create a new case" (small, muted)
  - A "New Case" button (sky-500)
- Apply the same pattern to clients and knowledge empty states.

## Constraints

- Don't change any API calls or backend code.
- Don't break existing functionality — these are purely visual changes.
- Keep all styling consistent with the existing design system (sky-500 primary, slate tones, rounded-xl cards).
- If you need new shadcn/ui components, install them.
- Run `npx tsc --noEmit` from `frontend/` to verify no TypeScript errors.
