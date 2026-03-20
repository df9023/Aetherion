# Claude Code Prompt: MVP Frontend Completion

You are working on **Aetherion**, an AI-native decision workspace for Swedish pension advisory. The backend (FastAPI) and frontend (Next.js 14 + shadcn/ui + Tailwind) are both functional. The frontend currently has read-only pages wired to the real API. Your job is to complete the MVP by adding create flows, a client detail page, case status transitions, breadcrumb fix, and error handling.

## Design System (already in place — follow it exactly)

- **Colors**: Dark sidebar (`bg-slate-950`), white cards with `border-slate-200/60`, sky-500 for primary actions
- **Cards**: `rounded-xl border border-slate-200/60 bg-white p-5 shadow-sm` with `hover:border-slate-300 hover:shadow-md`
- **Buttons**: Primary: `bg-sky-500 hover:bg-sky-600 text-white rounded-lg`. Secondary: `variant="outline" rounded-lg`
- **Section headers**: `text-xs font-medium uppercase tracking-wider text-muted-foreground`
- **Badges/pills**: `rounded-full px-2.5 py-0.5 text-xs font-medium` with color variants per status
- **Font**: Inter (already configured)
- **Icons**: Lucide React (already installed)

## Existing infrastructure you MUST use

- **API client**: `frontend/lib/api.ts` — exports `apiFetch<T>(path, options)` and `apiDownload(path)`. Adds dev auth headers automatically.
- **React Query hooks**: `frontend/lib/hooks.ts` — all existing hooks use `useQuery`/`useMutation` from `@tanstack/react-query`.
- **Labels/styles**: `frontend/lib/labels.ts` — maps for `caseTypeLabels`, `statusStyles`, `statusLabels`, `categoryStyles`, `categoryLabels`, etc.
- **Providers**: `frontend/components/providers.tsx` — `QueryClientProvider` already wrapping the app.
- **Toast**: `sonner` already installed and `<Toaster />` in the dashboard layout. Use `toast.success()` / `toast.error()`.

## shadcn/ui components already installed

button, input, select, textarea, badge, card, tabs, accordion, avatar, breadcrumb, progress, separator, skeleton, tooltip, sonner

You may install additional shadcn/ui components if needed (e.g. `dialog`, `label`, `dropdown-menu`). Use: `npx shadcn@latest add <component>` from the `frontend/` directory.

---

## Task 1: Add missing shadcn/ui components

Install these (you'll need them for modals and forms):

```bash
cd frontend
npx shadcn@latest add dialog label dropdown-menu
```

---

## Task 2: Add hooks for create/update operations

In `frontend/lib/hooks.ts`, add these hooks (follow the exact pattern of existing hooks):

### useCreateClient
```typescript
export function useCreateClient() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: {
      name: string
      date_of_birth: string        // "YYYY-MM-DD"
      employment_status: string    // "employed" | "self_employed" | "retired" | "other"
      collective_agreement: string // "ITP1" | "ITP2" | "SAF_LO" | "KAP_KL" | "AKAP_KL" | "PA16" | "other" | "none"
      employer_name?: string
      annual_income?: number
      desired_retirement_age?: number
      risk_profile?: string        // "low" | "moderate" | "high"
    }) => apiFetch<ClientResponse>("/clients", {
      method: "POST",
      body: JSON.stringify(data),
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clients"] })
    },
  })
}
```

### useCreateCase
```typescript
export function useCreateCase() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: {
      title: string
      case_type: string
      client_id: string
      assigned_to: string
      summary?: string
      meeting_date?: string
    }) => apiFetch<CaseResponse>("/cases", {
      method: "POST",
      body: JSON.stringify(data),
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cases"] })
    },
  })
}
```

### useUpdateCase
```typescript
export function useUpdateCase(caseId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: {
      title?: string
      case_type?: string
      status?: string
      summary?: string
      assigned_to?: string
    }) => apiFetch<CaseResponse>(`/cases/${caseId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cases"] })
      queryClient.invalidateQueries({ queryKey: ["cases", caseId] })
    },
  })
}
```

### useClientCases (for client detail page)
```typescript
export function useClientCases(clientId: string) {
  const { data: cases } = useCases()
  // Filter client-side since there's no dedicated endpoint
  const clientCases = cases?.filter(c => c.client_id === clientId) ?? []
  return { data: clientCases, isLoading: !cases }
}
```

---

## Task 3: Create Client Dialog

Create `frontend/components/create-client-dialog.tsx`:

- A `<Dialog>` component triggered by a button (receives `trigger` as children or wraps a `<Button>`).
- Form fields (use `<Label>` + `<Input>` / `<Select>` from shadcn/ui):
  - **Name** (text, required)
  - **Date of Birth** (date input, required)
  - **Employment Status** (select: Employed, Self-employed, Retired, Other — values: `employed`, `self_employed`, `retired`, `other`) (required)
  - **Employer Name** (text, optional)
  - **Collective Agreement** (select: ITP1, ITP2, SAF-LO, KAP-KL, AKAP-KL, PA16, Other, None — values match the enum) (required)
  - **Annual Income** (number input, optional, in SEK)
  - **Desired Retirement Age** (number input, optional)
  - **Risk Profile** (select: Low, Moderate, High — values: `low`, `moderate`, `high`) (optional)
- Uses `useCreateClient()` mutation.
- On success: `toast.success("Client created")`, close dialog, form resets.
- On error: `toast.error(err.message)`.
- Submit button: primary style, disabled while `isPending`, shows `<Loader2 className="animate-spin" />` when loading.
- Use a two-column grid for the form fields to keep it compact.

---

## Task 4: Create Case Dialog

Create `frontend/components/create-case-dialog.tsx`:

- A `<Dialog>` component.
- Form fields:
  - **Client** (select, required — populated from `useClients()` hook, showing client name, value is client ID)
  - **Case Type** (select, required — use entries from `caseTypeLabels` in `lib/labels.ts`)
  - **Title** (text, required)
  - **Summary** (textarea, optional)
- On submit, use `useCreateCase()`. The `assigned_to` field should be set to `process.env.NEXT_PUBLIC_DEV_USER_ID` (the current dev user).
- On success: `toast.success("Case created")`, close dialog, navigate to the new case: `router.push(`/cases/${result.id}`)`.
- On error: `toast.error(err.message)`.
- Use `useRouter` from `next/navigation` for redirect.

---

## Task 5: Wire up "New" buttons

### Cases page (`frontend/app/(dashboard)/cases/page.tsx`)
Replace the stub `<Button>` for "New Case" with the `<CreateCaseDialog>` component. The dialog's trigger should be styled as the existing button (sky-500, with Plus icon).

### Clients page (`frontend/app/(dashboard)/clients/page.tsx`)
Replace the stub `<Button>` for "New Client" with the `<CreateClientDialog>` component. Same styling.

---

## Task 6: Client Detail Page

Create `frontend/app/(dashboard)/clients/[id]/page.tsx`:

Layout: similar to case detail — a main content area (no need for two columns; single column is fine).

Sections:
1. **Client Header Card** — Name (large), initials avatar, date of birth & age, employment status badge.
2. **Details Card** — Two-column grid showing:
   - Employer
   - Collective Agreement (badge, blue)
   - Annual Income (formatted in SEK)
   - Monthly Income (annual / 12, formatted)
   - Desired Retirement Age
   - Risk Profile (colored badge: green=low, amber=moderate, red=high)
   - Employment Status
3. **Linked Cases Card** — Use `useClientCases(id)`. Show a list of cases (same card style as the cases list page) linking to `/cases/{case_id}`. Show "No cases yet" empty state with a button to create a new case (opens CreateCaseDialog with client pre-selected — pass `defaultClientId` prop).

Use `useClient(id)` to fetch client data. Show skeleton loaders while loading. Show "Client not found" for 404.

### Make client cards clickable
In `frontend/app/(dashboard)/clients/page.tsx`, wrap each client card in `<Link href={`/clients/${c.id}`}>`.

---

## Task 7: Case Status Transitions

In the **case detail page** (`frontend/app/(dashboard)/cases/[id]/page.tsx`):

Add a `<DropdownMenu>` next to the status badge in the Case Header card. The dropdown shows valid next statuses based on the current status:

```
Status transition rules:
  draft → in_preparation
  in_preparation → ready_for_review
  ready_for_review → in_review
  in_review → approved, rejected (rejected → in_preparation)
  approved → completed
  completed → archived
```

Use `useUpdateCase(id)` to PATCH the status. On success, toast the new status. On error, toast the error.

The trigger should be a small button/icon next to the status badge (e.g., a `ChevronDown` icon or make the status badge itself clickable). Only show the dropdown if there are valid transitions.

Define the transition map as a const:
```typescript
const STATUS_TRANSITIONS: Record<string, string[]> = {
  draft: ["in_preparation"],
  in_preparation: ["ready_for_review"],
  ready_for_review: ["in_review"],
  in_review: ["approved"],
  approved: ["completed"],
  completed: ["archived"],
}
```

---

## Task 8: Fix Breadcrumbs

In `frontend/components/top-bar.tsx`:

The current implementation imports `mockCases` to look up case titles. This doesn't work with real data.

Replace the mock lookup with the `useCase` hook:
- Extract the case ID from the URL segments.
- Call `useCase(segments[1])` only when `segments[0] === "cases" && segments[1]`.
- Similarly, for clients detail, call `useClient(segments[1])` when `segments[0] === "clients" && segments[1]`.
- Show the case title or client name in the breadcrumb.
- While loading, show a skeleton or the ID as placeholder.
- Remove the `import { mockCases } from "@/lib/mock-data"` import.

Add breadcrumb support for the clients detail route:
```
/clients → "Clients"
/clients/[id] → "Clients" > "Client Name"
```

---

## Task 9: Fix existing bugs

1. **`frontend/app/(dashboard)/knowledge/page.tsx`**: There's a `class=` that should be `className=` on the tag spans. Also `Skeleton invalid` has a stray `invalid` prop — remove it.

2. **`frontend/lib/mock-data.ts`**: This file has duplicate label/style maps that are also in `lib/labels.ts`. Leave the mock data objects in place (they serve as fallback/reference) but do NOT import labels from mock-data anywhere — always use `lib/labels.ts`.

3. **`frontend/components/top-bar.tsx`**: Remove the `mockCases` import (done as part of Task 8).

---

## Task 10: Global error handling

Wrap the `QueryClient` in `frontend/components/providers.tsx` with a global `onError` handler:

```typescript
new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30000, retry: 1 },
    mutations: {
      onError: (error: Error) => {
        toast.error(error.message || "Something went wrong")
      },
    },
  },
})
```

Import `toast` from `sonner` in providers.tsx.

---

## Verification Checklist

After completing all tasks, verify:

1. [ ] `/cases` — "New Case" button opens dialog, form submits, redirects to new case
2. [ ] `/clients` — "New Client" button opens dialog, form submits, client appears in list
3. [ ] `/clients` — Client cards are clickable, link to `/clients/[id]`
4. [ ] `/clients/[id]` — Shows client details, linked cases, "Create Case" button
5. [ ] `/cases/[id]` — Status badge has dropdown to change status
6. [ ] Breadcrumbs show real case title and client name (not mock data or UUID)
7. [ ] No TypeScript errors (`npx tsc --noEmit` from frontend/)
8. [ ] No `class=` in TSX (should be `className=`)
9. [ ] All toast messages working on success and error

## Important Notes

- **Do NOT modify** any backend files. The backend API is complete for this scope.
- **Do NOT create** new API endpoints. Use only existing ones.
- Keep all styling consistent with the existing design system.
- Use `"use client"` directive on all page/component files that use hooks or interactivity.
- The dev user ID is available at `process.env.NEXT_PUBLIC_DEV_USER_ID` — use this for `assigned_to` when creating cases.
