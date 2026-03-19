# Claude Code Prompt — Wire Frontend to Real Backend API

## Goal

Replace all mock data in the Aetherion frontend with real API calls to the FastAPI backend at `http://localhost:8000/api/v1`. After this, the full demo loop works end-to-end: advisor sees real cases, clicks "Generate Recommendation", gets a real AI-generated recommendation from Claude, generates a document, and downloads the PDF.

**Prerequisites**: Backend is running (`docker compose up -d` for DB, `cd backend && uvicorn app.main:app --reload`), seed data exists (`python -m scripts.seed`), frontend is running (`cd frontend && npm run dev`).

---

## Part 1: Backend Changes (do these first)

### 1A. Dev Auth Bypass

The backend auth (`backend/app/api/deps.py`) requires JWT Bearer tokens. For development, add a bypass that accepts `X-Dev-User-Id` and `X-Dev-Org-Id` headers when `settings.debug` is `True`.

Modify `backend/app/api/deps.py` — change `get_current_user`:

```python
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(HTTPBearer(auto_error=False))],
    db: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    request: Request,
) -> User:
    # Dev bypass: if DEBUG=true and dev headers present, use those
    if settings.debug:
        dev_user_id = request.headers.get("X-Dev-User-Id")
        dev_org_id = request.headers.get("X-Dev-Org-Id")
        if dev_user_id:
            result = await db.execute(select(User).where(User.id == UUID(dev_user_id)))
            user = result.scalar_one_or_none()
            if user and user.is_active:
                return user

    # Normal JWT flow
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    # ... rest of JWT decode logic unchanged
```

Add `from fastapi import Request` to imports.

Then set `DEBUG=true` in `backend/.env`.

### 1B. Add Missing Endpoints

The frontend needs two endpoints that don't exist yet:

**1. List recommendations for a case** — `GET /cases/{case_id}/recommendations`

Add to `backend/app/api/v1/endpoints/cases.py`:

```python
@router.get("/{case_id}/recommendations", response_model=list[RecommendationResponse])
async def list_case_recommendations(
    case_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> list[Recommendation]:
    # Verify case belongs to org
    case_result = await db.execute(
        select(Case).where(Case.id == case_id, Case.organization_id == organization_id)
    )
    if not case_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Case not found")

    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.case_id == case_id)
        .order_by(Recommendation.version.desc())
    )
    return list(result.scalars().all())
```

Add `from app.models.recommendation import Recommendation` to imports if not already there.

**2. List evidence for a recommendation** — `GET /recommendations/{recommendation_id}/evidence`

Add to `backend/app/api/v1/endpoints/recommendations.py`:

```python
from app.models.evidence import Evidence
from app.schemas.evidence import EvidenceResponse

@router.get("/{recommendation_id}/evidence", response_model=list[EvidenceResponse])
async def list_recommendation_evidence(
    recommendation_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrganizationId,
) -> list[Evidence]:
    # Verify recommendation belongs to org via case
    result = await db.execute(
        select(Recommendation)
        .join(Case, Case.id == Recommendation.case_id)
        .where(
            Recommendation.id == recommendation_id,
            Case.organization_id == organization_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Recommendation not found")

    evidence_result = await db.execute(
        select(Evidence)
        .where(Evidence.recommendation_id == recommendation_id)
        .order_by(Evidence.created_at)
    )
    return list(evidence_result.scalars().all())
```

### 1C. Verify CORS

Check that `backend/app/main.py` has CORS allowing `http://localhost:3000`. It should already have this from the `cors_origins` setting — just verify.

---

## Part 2: Frontend — API Client & Hooks

### 2A. Create API Client

Create `frontend/lib/api.ts`:

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

// Dev auth headers — replace these UUIDs with real ones from your seed data.
// Run: cd backend && python -c "from scripts.seed import *; import asyncio; asyncio.run(main())"
// then check the database for actual user/org UUIDs.
// For now, we'll fetch them dynamically from the API on first load.
const DEV_HEADERS: Record<string, string> = {
  "X-Dev-User-Id": "", // Will be set after fetching
  "X-Dev-Org-Id": "",  // Will be set after fetching
}

let headersInitialized = false

async function initDevHeaders() {
  if (headersInitialized) return
  // We can't get these without auth, so they need to be hardcoded
  // or read from env. For now, use NEXT_PUBLIC env vars.
  DEV_HEADERS["X-Dev-User-Id"] = process.env.NEXT_PUBLIC_DEV_USER_ID || ""
  DEV_HEADERS["X-Dev-Org-Id"] = process.env.NEXT_PUBLIC_DEV_ORG_ID || ""
  headersInitialized = true
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  await initDevHeaders()
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...DEV_HEADERS,
      ...options.headers,
    },
  })
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail || `API error: ${res.status}`)
  }
  return res.json()
}

export async function apiDownload(path: string): Promise<Blob> {
  await initDevHeaders()
  const res = await fetch(`${API_BASE}${path}`, {
    headers: DEV_HEADERS,
  })
  if (!res.ok) {
    throw new Error(`Download failed: ${res.status}`)
  }
  return res.blob()
}
```

### 2B. Create React Query Hooks

Create `frontend/lib/hooks.ts`:

```typescript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiFetch, apiDownload } from "./api"

// Types (match backend schemas)
export interface CaseResponse { id: string; title: string; case_type: string; status: string; summary: string | null; meeting_date: string | null; client_id: string; assigned_to: string; organization_id: string; created_at: string; updated_at: string; completed_at: string | null }
export interface ClientResponse { id: string; name: string; date_of_birth: string; employment_status: string; collective_agreement: string; external_id: string | null; employer_name: string | null; annual_income: string | null; desired_retirement_age: number | null; risk_profile: string | null; organization_id: string; created_at: string; updated_at: string; created_by: string }
export interface RecommendationResponse { id: string; case_id: string; recommendation_type: string; summary: string; reasoning_chain: { step: number; description: string; evidence_ids: string[]; conclusion: string }[]; assumptions: { assumption: string; basis: string; impact_if_wrong: string }[]; scenarios: { name: string; description: string; projected_outcome: Record<string, any> }[] | null; suitability_score: string | null; version: number; status: string; created_at: string; created_by: string; approved_by: string | null }
export interface EvidenceResponse { id: string; recommendation_id: string; source_type: string; source_reference: string; content_snippet: string; relevance_explanation: string; confidence: string; created_at: string }
export interface KnowledgeItemResponse { id: string; title: string; content: string; category: string; source: string; tags: string[]; effective_date: string | null; expiry_date: string | null; organization_id: string; is_active: boolean; created_at: string; updated_at: string; created_by: string; approved_by: string | null }
export interface AuditEntryResponse { id: string; case_id: string; action: string; actor_id: string; actor_type: string; details: Record<string, any>; ip_address: string | null; timestamp: string }
export interface DocumentResponse { id: string; document_type: string; title: string; file_format: string; case_id: string; recommendation_id: string | null; file_path: string; generated_at: string; generated_by: string; version: number }

// Cases
export function useCases() {
  return useQuery({ queryKey: ["cases"], queryFn: () => apiFetch<CaseResponse[]>("/cases") })
}

export function useCase(id: string) {
  return useQuery({ queryKey: ["cases", id], queryFn: () => apiFetch<CaseResponse>(`/cases/${id}`) })
}

// Clients
export function useClients() {
  return useQuery({ queryKey: ["clients"], queryFn: () => apiFetch<ClientResponse[]>("/clients") })
}

export function useClient(id: string) {
  return useQuery({ queryKey: ["clients", id], queryFn: () => apiFetch<ClientResponse>(`/clients/${id}`), enabled: !!id })
}

// Recommendations for a case
export function useCaseRecommendations(caseId: string) {
  return useQuery({ queryKey: ["cases", caseId, "recommendations"], queryFn: () => apiFetch<RecommendationResponse[]>(`/cases/${caseId}/recommendations`), enabled: !!caseId })
}

// Evidence for a recommendation
export function useRecommendationEvidence(recId: string) {
  return useQuery({ queryKey: ["recommendations", recId, "evidence"], queryFn: () => apiFetch<EvidenceResponse[]>(`/recommendations/${recId}/evidence`), enabled: !!recId })
}

// Generate recommendation (mutation)
export function useGenerateRecommendation(caseId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (additionalContext?: string) =>
      apiFetch<RecommendationResponse>(`/cases/${caseId}/generate-recommendation`, {
        method: "POST",
        body: JSON.stringify({ additional_context: additionalContext || null }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cases", caseId, "recommendations"] })
      queryClient.invalidateQueries({ queryKey: ["cases", caseId, "audit"] })
    },
  })
}

// Audit trail
export function useCaseAudit(caseId: string) {
  return useQuery({ queryKey: ["cases", caseId, "audit"], queryFn: () => apiFetch<AuditEntryResponse[]>(`/cases/${caseId}/audit`), enabled: !!caseId })
}

// Knowledge search
export function useKnowledgeSearch(query: string) {
  return useQuery({
    queryKey: ["knowledge", "search", query],
    queryFn: () => apiFetch<KnowledgeItemResponse[]>("/knowledge/search", { method: "POST", body: JSON.stringify({ query, limit: 10 }) }),
    enabled: query.length >= 2,
  })
}

// Knowledge list (for the knowledge page)
export function useKnowledge() {
  return useQuery({ queryKey: ["knowledge"], queryFn: () => apiFetch<KnowledgeItemResponse[]>("/knowledge") })
}

// Generate document (mutation)
export function useGenerateDocument(recommendationId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (fileFormat: "pdf" | "docx" = "pdf") =>
      apiFetch<DocumentResponse>(`/recommendations/${recommendationId}/generate-document`, {
        method: "POST",
        body: JSON.stringify({ file_format: fileFormat }),
      }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["cases", data.case_id, "audit"] })
    },
  })
}

// Download document
export async function downloadDocument(documentId: string, filename: string) {
  const blob = await apiDownload(`/documents/${documentId}/download`)
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
```

### 2C. Setup React Query Provider

Create `frontend/components/providers.tsx`:

```typescript
"use client"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { useState } from "react"

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: { queries: { staleTime: 30000, retry: 1 } },
  }))
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
}
```

Wrap the dashboard layout in `app/(dashboard)/layout.tsx` with `<Providers>`:

```tsx
import { Providers } from "@/components/providers"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <Providers>
      <div className="min-h-screen bg-slate-50">
        <Sidebar />
        <div className="ml-64 min-h-screen">
          <TopBar />
          <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
        </div>
      </div>
    </Providers>
  )
}
```

---

## Part 3: Frontend — Update Pages

### 3A. Cases Dashboard (`app/(dashboard)/cases/page.tsx`)

Replace mock data imports with the `useCases` hook:

- `const { data: cases, isLoading } = useCases()`
- Show `<Skeleton>` cards when `isLoading`
- Keep the filter/search logic but operate on `cases ?? []`
- Keep the `statusStyles`, `statusLabels`, `caseTypeLabels` helper maps (move to a `lib/labels.ts` utility if they aren't already in `mock-data.ts`)

### 3B. Case Detail (`app/(dashboard)/cases/[id]/page.tsx`)

This is the biggest change. Replace all mock data with hooks:

```typescript
const { data: caseData, isLoading: caseLoading } = useCase(id)
const { data: client, isLoading: clientLoading } = useClient(caseData?.client_id ?? "")
const { data: recommendations } = useCaseRecommendations(id)
const recommendation = recommendations?.[0] // Latest version
const { data: evidence } = useRecommendationEvidence(recommendation?.id ?? "")
const { data: auditEntries } = useCaseAudit(id)
const generateRec = useGenerateRecommendation(id)
const generateDoc = useGenerateDocument(recommendation?.id ?? "")
```

The AI Recommendation section now has three real states:
1. **No recommendation**: `recommendations` is empty → show generate UI
2. **Generating**: `generateRec.isPending` → show loading steps
3. **Has recommendation**: `recommendation` exists → show viewer

Wire up the buttons:
- "Generate Recommendation" calls `generateRec.mutate(additionalContext)`
- "Generate Document" calls `generateDoc.mutate("pdf")`
- "Download PDF" calls `downloadDocument(doc.id, doc.title + ".pdf")`
- "Generate New Version" calls `generateRec.mutate(additionalContext)` again

For the knowledge search panel, use `useKnowledgeSearch` with a debounced search input (300ms debounce).

### 3C. Clients Page (`app/(dashboard)/clients/page.tsx`)

Replace mock data with `useClients()`. Show skeleton cards while loading.

### 3D. Knowledge Page (`app/(dashboard)/knowledge/page.tsx`)

Replace mock data with `useKnowledge()` for the full list. The category tabs filter client-side from the full list. Show skeleton cards while loading.

---

## Part 4: Environment Variables

Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_DEV_USER_ID=<UUID of Erik Eriksson from seed>
NEXT_PUBLIC_DEV_ORG_ID=<UUID of NordPension from seed>
```

To get the UUIDs, run against the database:

```sql
SELECT id FROM users WHERE name = 'Erik Eriksson';
SELECT id FROM organizations LIMIT 1;
```

Or read them from the seed script output / backend logs.

---

## Part 5: Verify

After all changes, test the full demo loop:

1. Open `http://localhost:3000` → cases dashboard loads from API
2. Click case → detail page loads case + client from API
3. If no recommendation: click "Generate Recommendation" → calls Claude → recommendation appears
4. Recommendation shows reasoning, evidence, scenarios, score — all from real API data
5. Click "Generate Document" → creates PDF on server
6. Click "Download PDF" → file downloads
7. Audit trail updates in real-time after each action
8. Knowledge search returns real results from pgvector

If the Anthropic API key isn't set, the generate endpoint returns 503 — that's expected. Set `ANTHROPIC_API_KEY` in `backend/.env` for the full AI demo.

---

## Important Notes

- Keep the label/style maps (`statusStyles`, `caseTypeLabels`, etc.) from `mock-data.ts` — move them to a `lib/labels.ts` file. Only remove the mock data arrays.
- Add proper error handling: show toast (shadcn Sonner) on mutation errors.
- The `mock-data.ts` file can be kept as a fallback reference but should no longer be imported by any page.
- Don't change any visual styling — the design is final. Only change data sources.
