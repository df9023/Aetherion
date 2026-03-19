# v0 Prompt — Aetherion Workbench UI

> **CRITICAL DESIGN INSTRUCTION**: This must look like a premium, modern tech product — think Linear, Vercel Dashboard, or Legora (legora.com). It must NOT look like a basic HTML page. Use the shadcn/ui "New York" style variant. Use `font-sans` (Geist Sans or Inter via `next/font`). NEVER use serif fonts like Times New Roman. Every surface must have intentional styling.

## What to build

Build the **Workbench** — the advisor-facing workspace for Aetherion, an AI-native decision platform for pension and retirement institutions. This is a full Next.js 14 app (App Router) using **shadcn/ui (New York style)**, **Tailwind CSS**, and **React Query** (`@tanstack/react-query`). The backend is a FastAPI API at `http://localhost:8000/api/v1`.

The target user is a Swedish pension advisor at a firm like Max Matthiessen or SPP. They use this daily to prepare cases, generate AI recommendations, review compliance, and produce client-ready documentation.

---

## Design System — Legora-inspired Modern SaaS

This must look and feel like **Legora** (legora.com) — a premium Swedish AI platform. Clean, dark, sophisticated, tech-forward. NOT a generic template. NOT a basic HTML page.

### Font Stack (MANDATORY)

```tsx
// app/layout.tsx — use next/font
import { Inter } from "next/font/google"
const inter = Inter({ subsets: ["latin"] })
// Apply: <body className={`${inter.className} antialiased`}>
```

- **NEVER** use Times New Roman, Georgia, or any serif font
- Body: `Inter` 14px, `text-sm` in Tailwind
- Headings: `Inter` semibold/bold, `tracking-tight`
- Page titles: `text-3xl font-bold tracking-tight`
- Section headings: `text-lg font-semibold`
- Small labels: `text-xs font-medium uppercase tracking-wider text-muted-foreground`

### Color System (Tailwind CSS variables)

Configure these in your `globals.css` using shadcn/ui CSS variables:

```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222 47% 11%;      /* slate-900 */
    --card: 0 0% 100%;
    --card-foreground: 222 47% 11%;
    --primary: 199 89% 48%;          /* sky-500 — the accent */
    --primary-foreground: 0 0% 100%;
    --secondary: 210 40% 96%;        /* slate-100 */
    --secondary-foreground: 222 47% 11%;
    --muted: 210 40% 96%;
    --muted-foreground: 215 16% 47%; /* slate-500 */
    --accent: 210 40% 96%;
    --accent-foreground: 222 47% 11%;
    --destructive: 0 84% 60%;
    --border: 214 32% 91%;           /* slate-200 */
    --ring: 199 89% 48%;
    --radius: 0.75rem;
  }
}
```

- **Page backgrounds**: `bg-slate-50` (not pure white — slight warm gray)
- **Cards**: `bg-white` with `border border-slate-200/60 shadow-sm rounded-xl`
- **Sidebar**: `bg-slate-950` (near-black) with `text-slate-300` nav items
- **Sidebar active**: `bg-sky-500/10 text-sky-400 border-l-2 border-sky-400`
- **Sidebar hover**: `bg-slate-800/50 text-slate-100`
- **Accent/CTA buttons**: `bg-sky-500 hover:bg-sky-600 text-white` — rounded-lg, not fully rounded
- **Secondary buttons**: `bg-slate-100 hover:bg-slate-200 text-slate-700`
- **Status badges** — use shadcn Badge with custom variants:
  - Draft: `bg-slate-100 text-slate-600`
  - In preparation: `bg-blue-50 text-blue-700 border border-blue-200`
  - Ready for review: `bg-amber-50 text-amber-700 border border-amber-200`
  - Approved: `bg-emerald-50 text-emerald-700 border border-emerald-200`
  - Completed: `bg-green-50 text-green-800 border border-green-200`

### Layout Patterns

- **Sidebar**: Fixed left, `w-64`, full height `h-screen`, `bg-slate-950`. Sticky.
- **Main content**: `ml-64 min-h-screen bg-slate-50`
- **Content wrapper**: `max-w-7xl mx-auto px-6 py-8`
- **Card spacing**: `space-y-6` between cards, `p-6` internal padding
- **Card style**: `bg-white rounded-xl border border-slate-200/60 shadow-sm`
- **Two-column case detail**: Use CSS Grid — `grid grid-cols-[1fr_400px] gap-6`

### Component Styling Rules

- **Cards**: Always `rounded-xl`, never `rounded` or `rounded-md`. Subtle `shadow-sm`. Border `border-slate-200/60`.
- **Buttons**: `rounded-lg` (not fully round). Primary = `bg-sky-500`. Height `h-10` for normal, `h-12` for hero CTAs.
- **Inputs**: `rounded-lg bg-slate-50 border-slate-200 focus:ring-sky-500`
- **Badges**: Small, `rounded-full`, `text-xs font-medium`, `px-2.5 py-0.5`
- **Tables**: Use `text-sm`, header row `text-xs uppercase tracking-wider text-muted-foreground bg-slate-50`
- **Hover on cards**: `hover:shadow-md hover:border-slate-300 transition-all duration-200`
- **Skeleton loaders**: Use shadcn `Skeleton` component with `rounded-lg` during data loading
- **Icons**: Lucide React, size `16-18px` (`w-4 h-4`), color `text-slate-400` unless active
- **Separators**: `border-slate-100`, very subtle

### What It Must NOT Look Like

- **NO serif fonts** — no Times New Roman, no Georgia, no default browser font
- **NO unstyled HTML** — every element must have explicit Tailwind classes
- **NO bright gradients or neon colors**
- **NO generic Bootstrap/Material look**
- **NO heavy borders or boxy layouts**
- **NO comic sans, papyrus, or any novelty fonts**
- **NO default browser link styling** (blue underlined links)
- If it looks like a 2005 website or a plain HTML form, you've failed

---

## Pages & Components

### 1. App Shell / Layout

A persistent layout wrapping all pages.

**Left sidebar** — `fixed left-0 top-0 h-screen w-64 bg-slate-950 text-slate-300 flex flex-col`:

```
┌──────────────────────┐
│  ◆ Aetherion         │  ← Logo: text-lg font-bold text-white, small diamond icon
│                      │
│  ━━━━━━━━━━━━━━━━━━  │  ← Separator: border-slate-800
│                      │
│  📋 Cases            │  ← Active: bg-sky-500/10 text-sky-400 border-l-2 border-sky-400
│  👥 Clients          │  ← Inactive: text-slate-400 hover:bg-slate-800/50 hover:text-slate-100
│  📖 Knowledge Base   │  ← Each: px-4 py-2.5 flex items-center gap-3 text-sm font-medium
│                      │
│                      │
│  ━━━━━━━━━━━━━━━━━━  │
│  [Avatar] Erik E.    │  ← Bottom: mt-auto p-4, Avatar + name + "Advisor" role badge
│  Advisor       ⚙️    │     Settings gear icon right-aligned
└──────────────────────┘
```

- Use Lucide icons: `Briefcase` for Cases, `Users` for Clients, `BookOpen` for Knowledge Base, `Settings` for settings
- Nav items: `rounded-lg mx-2` for the hover/active background
- Logo area: `p-6` padding, just text wordmark, no image

**Top bar** — `sticky top-0 z-10 h-14 bg-white/80 backdrop-blur-sm border-b border-slate-200/60 flex items-center justify-between px-6`:
- Left: Breadcrumb using shadcn `Breadcrumb` — `text-sm text-muted-foreground`, active segment `text-foreground font-medium`
- Right: Org badge ("NordPension Rådgivning AB") as `text-xs font-medium text-slate-500 bg-slate-100 px-3 py-1 rounded-full` (org name stays Swedish — it's a proper noun)

**Main content area** — `ml-64 min-h-screen bg-slate-50`

### 2. Cases Dashboard (`/cases`)

The main landing page. Wrap in `max-w-7xl mx-auto px-6 py-8`.

**Header area** — `flex items-center justify-between mb-8`:
- Left: 
  - Page title: `text-3xl font-bold tracking-tight text-slate-900` — "Cases"
  - Subtitle: `text-sm text-muted-foreground mt-1` — "Manage and track advisory cases"
- Right: `Button` accent — `bg-sky-500 hover:bg-sky-600 text-white rounded-lg h-10 px-4 text-sm font-medium` with `Plus` icon (`w-4 h-4 mr-2`). Label: "New Case"

**Filters row** — `flex items-center gap-3 mb-6`:
- Search input: `w-80 bg-white rounded-lg border-slate-200` with `Search` icon inside, placeholder "Search cases..."
- Status filter: shadcn `Select` — `w-48`, options: All, Draft, In Preparation, Ready for Review, In Review, Approved, Completed, Archived
- Case type filter: shadcn `Select` — `w-48`

**Cases list** — `space-y-3`. Each case is a card, NOT a raw table:

```
┌──────────────────────────────────────────────────────────────────┐
│  Anna Johansson — Retirement Planning                    2d ago │
│  text-base font-semibold                   text-xs text-slate-400│
│                                                                  │
│  [Retirement Planning]  [In Preparation]       Erik Eriksson    │
│  badge slate             badge blue            text-sm slate-500 │
└──────────────────────────────────────────────────────────────────┘
```

- Card: `bg-white rounded-xl border border-slate-200/60 shadow-sm p-5 hover:shadow-md hover:border-slate-300 transition-all duration-200 cursor-pointer`
- Case title: `text-base font-semibold text-slate-900`
- Client name shown in the title (part of the case title)
- Type badge: `bg-slate-100 text-slate-600 text-xs rounded-full px-2.5 py-0.5`
- Status badge: colored per status (see color system above)
- Date: `text-xs text-slate-400` right-aligned
- Assigned to: `text-sm text-slate-500` with small `User` icon
- Click → navigates to `/cases/[id]`

**API:**
```
GET /api/v1/cases → CaseResponse[]
```

```typescript
interface CaseResponse {
  id: string
  title: string
  case_type: "pension_review" | "transfer_advice" | "salary_exchange" | "retirement_planning" | "survivor_protection" | "decumulation" | "other"
  status: "draft" | "in_preparation" | "ready_for_review" | "in_review" | "approved" | "completed" | "archived"
  summary: string | null
  meeting_date: string | null
  client_id: string
  assigned_to: string
  organization_id: string
  created_at: string
  updated_at: string
  completed_at: string | null
}
```

### 3. Case Detail (`/cases/[id]`)

The core workspace. This is where the advisor spends most of their time.

**Layout:** Two or three-column layout on large screens:
- **Left column (~60-65%)**: Main case content
- **Right column (~35-40%)**: Contextual panels (knowledge search, audit trail)

#### Left Column

**Case header card:**
- Case title (large, editable inline or via modal)
- Status badge (color-coded, same as dashboard)
- Case type badge
- Meeting date (if set)
- "Assigned to: Erik Eriksson"

**Client info card** (below case header):
- Client name (bold)
- Date of birth → show age in parentheses
- Employer + collective agreement badge (e.g., "Volvo — ITP1")
- Monthly income (formatted with SEK, thousand separators: "57 000 kr/mån")
- Risk profile badge: color-coded (`low` → green, `moderate` → amber, `high` → red)
- Desired retirement age
- Employment status

**API:**
```
GET /api/v1/clients/{client_id} → ClientResponse
```

```typescript
interface ClientResponse {
  id: string
  name: string
  date_of_birth: string // "1980-03-15"
  employment_status: "employed" | "self_employed" | "retired" | "other"
  collective_agreement: "ITP1" | "ITP2" | "SAF_LO" | "KAP_KL" | "AKAP_KL" | "PA16" | "other" | "none"
  external_id: string | null
  employer_name: string | null
  annual_income: string | null // decimal string
  desired_retirement_age: number | null
  risk_profile: "low" | "moderate" | "high" | null
  organization_id: string
  created_at: string
  updated_at: string
  created_by: string
}
```

**Generate Recommendation section:**

A hero card — this is the primary CTA of the entire product. Make it stand out:

- Card: `bg-white rounded-xl border border-slate-200/60 shadow-sm p-8`
- If no recommendation exists yet:
  - Small icon: `Sparkles` from Lucide, `w-8 h-8 text-sky-500 mb-3`
  - Heading: `text-xl font-semibold text-slate-900` — "AI Recommendation"
  - Description: `text-sm text-muted-foreground mt-1 mb-6` — "Generate a structured, evidence-based recommendation powered by AI"
  - Optional textarea: shadcn `Textarea` — `bg-slate-50 rounded-lg`, placeholder "Additional context for the AI (optional)..."
  - CTA button: `h-12 px-8 bg-sky-500 hover:bg-sky-600 text-white rounded-lg text-sm font-semibold` with `Sparkles` icon. Label: "Generate Recommendation"
  - **Loading state** (when clicked): Replace the button with a multi-step progress indicator:
    - Three steps shown vertically with animated transitions:
    - `✓ Retrieving knowledge...` (fade in, checkmark after 2s)
    - `◻ Analyzing case...` (animate in after step 1)
    - `◻ Building recommendation...` (animate in after step 2)
    - Use a subtle shimmer/pulse animation on the active step
    - Total generation takes 5-15 seconds

**API:**
```
POST /api/v1/cases/{case_id}/generate-recommendation
Body: { "additional_context": "string or null" }
→ RecommendationResponse
```

- If a recommendation exists: show the Recommendation Viewer (below)

#### Recommendation Viewer

Once generated, replace the generate section with a rich, structured recommendation display. This is the most important visual in the entire app.

**Recommendation header card** — `bg-white rounded-xl border border-slate-200/60 shadow-sm p-6`:
- Top row: `flex items-center justify-between`
  - Left: `text-xl font-semibold` — "Rekommendation v{version}"
  - Right: Status badge + Recommendation type badge
- **Suitability score** — prominent visual element:
  - Display as a large number: `text-4xl font-bold` with `/10` in `text-lg text-muted-foreground`
  - Color: `text-emerald-600` for 8-10, `text-amber-600` for 6-7.9, `text-red-600` for <6
  - Below: label `text-xs uppercase tracking-wider text-muted-foreground` — "Suitability Score"
  - A thin colored progress bar beneath showing the score visually

**Summary section** — `mt-6`:
- Label: `text-xs uppercase tracking-wider text-muted-foreground mb-2` — "Summary"
- Text: `text-sm text-slate-700 leading-relaxed`

**Reasoning chain** — use shadcn `Accordion` with custom styling:
- Section label: `text-xs uppercase tracking-wider text-muted-foreground mb-3` — "Reasoning"
- Each step as an accordion item with a visual stepper on the left:
  - Step number in a `w-7 h-7 rounded-full bg-sky-50 text-sky-600 text-xs font-bold flex items-center justify-center` circle
  - Vertical line connecting steps: `border-l-2 border-slate-100`
  - Description: `text-sm text-slate-800 font-medium`
  - Conclusion: `text-sm text-slate-500 mt-1`
  - Evidence badges: small pills `bg-blue-50 text-blue-700 text-xs rounded-full px-2 py-0.5` with `FileText` icon

**Assumptions** — collapsible section below reasoning:
- Section label: `text-xs uppercase tracking-wider text-muted-foreground mb-3` — "Assumptions"
- Each assumption as a small card: `bg-slate-50 rounded-lg p-4 space-y-2`
  - Assumption text: `text-sm font-medium text-slate-800`
  - Basis: `text-xs text-slate-500` with "Basis:" prefix
  - Impact if wrong: `text-xs text-amber-700 bg-amber-50 rounded-md p-2 mt-2` with `AlertTriangle` icon

**Scenarios** — cards in a grid `grid grid-cols-2 gap-4`:
- Section label: "Scenarios"
- Each scenario card: `bg-slate-50 rounded-lg p-5 border border-slate-100`
  - Name: `text-sm font-semibold text-slate-800`
  - Description: `text-xs text-slate-500 mt-1`
  - Projected outcome: key-value pairs with `text-xs`, keys in `font-medium text-slate-600`, values in `text-slate-800`

**Evidence section:**
- Section label: "Evidence"
- Each evidence item: `bg-white rounded-lg border border-slate-100 p-4`
  - Source type: badge like `bg-purple-50 text-purple-700 text-xs rounded-full`
  - Source reference: `text-sm font-medium text-slate-800`
  - Content snippet: `text-xs text-slate-500 line-clamp-2` (expandable on click)
  - Relevance: `text-xs text-slate-400 italic`
  - Confidence: thin progress bar (`bg-slate-100` track, `bg-sky-500` fill) + percentage label

**API for evidence:**
```
GET /api/v1/recommendations/{rec_id}/evidence → EvidenceResponse[]
```

```typescript
interface EvidenceResponse {
  id: string
  recommendation_id: string
  source_type: "product_rule" | "regulation" | "internal_policy" | "market_data" | "client_data" | "precedent" | "expert_knowledge"
  source_reference: string
  content_snippet: string
  relevance_explanation: string
  confidence: string // decimal 0-1
  created_at: string
}
```

**Actions bar** — `flex items-center gap-3 mt-6 pt-6 border-t border-slate-100`:
- "Generate Document" — `Button` secondary: `bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg h-10 text-sm` with `FileDown` icon
- "Download PDF" — `Button` outline: `border-slate-200 text-slate-700 rounded-lg h-10 text-sm` with `Download` icon (shown after doc generated)
- "Generate New Version" — `Button` ghost: `text-slate-500 hover:text-slate-700 rounded-lg h-10 text-sm` with `RefreshCw` icon, right-aligned with `ml-auto`

**Document generation API:**
```
POST /api/v1/recommendations/{rec_id}/generate-document
Body: { "file_format": "pdf" | "docx" }
→ DocumentResponse

GET /api/v1/documents/{doc_id}/download → file download
```

```typescript
interface DocumentResponse {
  id: string
  document_type: string
  title: string
  file_format: "docx" | "pdf"
  case_id: string
  recommendation_id: string
  file_path: string
  generated_at: string
  generated_by: string
  version: number
}
```

**Full RecommendationResponse shape:**
```typescript
interface ReasoningStep {
  step: number
  description: string
  evidence_ids: string[]
  conclusion: string
}

interface Assumption {
  assumption: string
  basis: string
  impact_if_wrong: string
}

interface Scenario {
  name: string
  description: string
  projected_outcome: Record<string, any>
}

interface RecommendationResponse {
  id: string
  case_id: string
  recommendation_type: "product_selection" | "allocation_change" | "transfer" | "salary_exchange" | "withdrawal_plan" | "coverage_change" | "other"
  summary: string
  reasoning_chain: ReasoningStep[]
  assumptions: Assumption[]
  scenarios: Scenario[] | null
  suitability_score: string | null // decimal
  version: number
  status: "draft" | "pending_review" | "approved" | "rejected" | "superseded"
  created_at: string
  created_by: string
  approved_by: string | null
}
```

#### Right Column

**Knowledge search panel** — `bg-white rounded-xl border border-slate-200/60 shadow-sm p-5`:
- Title: `text-sm font-semibold text-slate-800 mb-3` — "Knowledge Base"
- Search input: `bg-slate-50 rounded-lg border-slate-200 text-sm h-9` with `Search` icon (`w-4 h-4 text-slate-400`), placeholder "Search knowledge base..."
- Results: `space-y-2 mt-3`, each item:
  - `bg-slate-50 rounded-lg p-3 hover:bg-slate-100 transition-colors cursor-pointer`
  - Title: `text-sm font-medium text-slate-800`
  - Category badge: `text-xs rounded-full px-2 py-0.5 bg-slate-200 text-slate-600`
  - Tags as tiny pills: `text-[10px] bg-sky-50 text-sky-600 rounded-full px-1.5 py-0.5`
  - Expanding shows full content: `text-xs text-slate-600 leading-relaxed mt-2`

**API:**
```
POST /api/v1/knowledge/search
Body: { "query": "string", "limit": 10 }
→ KnowledgeItemResponse[]
```

```typescript
interface KnowledgeItemResponse {
  id: string
  title: string
  content: string
  category: "product_rule" | "internal_policy" | "regulatory_requirement" | "playbook" | "precedent" | "faq" | "process_guide"
  source: string
  tags: string[]
  effective_date: string | null
  expiry_date: string | null
  organization_id: string
  is_active: boolean
  created_at: string
  updated_at: string
  created_by: string
  approved_by: string | null
}
```

**Audit trail panel** — `bg-white rounded-xl border border-slate-200/60 shadow-sm p-5 mt-4`:
- Title: `text-sm font-semibold text-slate-800 mb-3` — "Audit Trail"
- Timeline layout with vertical line on the left:
  - Vertical line: `border-l-2 border-slate-100 ml-3`
  - Each entry: `flex gap-3 pb-4 relative`
    - Dot: `w-2.5 h-2.5 rounded-full bg-slate-300 mt-1.5 relative z-10` (green for approvals, blue for generation, gray for others)
    - Content:
      - Action: `text-xs font-medium text-slate-700`
      - Timestamp: `text-[10px] text-slate-400`
      - Actor type icon: tiny `User` or `Bot` icon
- Action labels:
  - `case_created` → "Case created"
  - `recommendation_generated` → "Recommendation generated by AI"
  - `recommendation_approved` → "Recommendation approved"
  - `document_generated` → "Document generated"
  - `compliance_check_passed` → "Compliance check passed"
  - `compliance_check_failed` → "Compliance check failed"

**API:**
```
GET /api/v1/cases/{case_id}/audit → AuditEntryResponse[]
```

```typescript
interface AuditEntryResponse {
  id: string
  case_id: string
  action: string
  actor_id: string
  actor_type: "user" | "system"
  details: Record<string, any>
  ip_address: string | null
  timestamp: string
}
```

### 4. Clients Page (`/clients`)

Wrap in `max-w-7xl mx-auto px-6 py-8`.

**Header**: Same pattern as Cases — "Clients" title, "New Client" button.

**Client cards** — `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4`:
Each card: `bg-white rounded-xl border border-slate-200/60 shadow-sm p-5 hover:shadow-md hover:border-slate-300 transition-all`
- Name: `text-base font-semibold text-slate-900`
- Age: `text-sm text-slate-500` — calculated from DOB, shown as "45 år"
- Employer + agreement: `text-sm text-slate-600` — "Volvo — ITP1"
- Risk profile badge:
  - Low: `bg-emerald-50 text-emerald-700 border border-emerald-200`
  - Moderate: `bg-amber-50 text-amber-700 border border-amber-200`
  - High: `bg-red-50 text-red-700 border border-red-200`
- Income: `text-sm text-slate-500` — formatted "57 000 kr/mån"

**API:**
```
GET /api/v1/clients → ClientResponse[]
```

### 5. Knowledge Base Page (`/knowledge`)

Wrap in `max-w-7xl mx-auto px-6 py-8`.

**Header**: "Knowledge Base" title.

**Search & filters** — `mb-6`:
- Large search input: `w-full max-w-xl bg-white rounded-lg border-slate-200 h-12 text-sm` with `Search` icon, placeholder "Search knowledge..."
- Category filter tabs below: use shadcn `Tabs` with `TabsList` — `bg-slate-100 rounded-lg p-1`:
  - Tab items: `text-xs font-medium rounded-md px-3 py-1.5`
  - Tabs: All, Product Rules, Internal Policy, Regulatory, Playbook, Precedent, FAQ, Process Guide

**Knowledge items** — `space-y-3`:
Each: `bg-white rounded-xl border border-slate-200/60 shadow-sm p-5`
- Title: `text-sm font-semibold text-slate-800`
- Category badge: colored per category
- Source: `text-xs text-slate-400`
- Tags: `flex gap-1.5 mt-2`, each tag `text-[10px] bg-sky-50 text-sky-600 rounded-full px-2 py-0.5 font-medium`
- Content excerpt: `text-xs text-slate-500 mt-2 line-clamp-3`
- Expandable with "Show more" link: `text-xs text-sky-500 hover:text-sky-600 font-medium cursor-pointer`

---

## Technical Details

### Auth Handling (dev stub)

The backend expects auth headers. For the prototype, hardcode dev headers on all API requests:

```typescript
const API_BASE = "http://localhost:8000/api/v1"

const defaultHeaders = {
  "Content-Type": "application/json",
  "X-User-Id": "DEV_USER_ID", // will be replaced with real UUID after seed
  "X-Organization-Id": "DEV_ORG_ID", // will be replaced with real UUID after seed
}
```

These will be replaced with real UUIDs from the seed data and eventually with WorkOS auth tokens.

### Data fetching

Use `@tanstack/react-query` for all API calls:
- `useQuery` for GETs with proper caching and refetch
- `useMutation` for POST/PATCH operations
- Show skeleton loaders during initial fetch
- Show toast notifications (shadcn `sonner`) on success/error for mutations

### Routing

Use Next.js App Router:
```
app/
  layout.tsx          → App shell (sidebar + top bar)
  cases/
    page.tsx          → Cases dashboard
    [id]/
      page.tsx        → Case detail
  clients/
    page.tsx          → Clients list
  knowledge/
    page.tsx          → Knowledge base
```

### UI Language

All UI chrome (navigation, labels, buttons, headings) is in **English**. Domain-specific Swedish terms that appear in the *data* stay as-is — these are proper nouns or industry terms (e.g., "ITP1", "ITP2", "löneväxling", "KAP-KL", organization/client names). Status labels:
- Draft, In Preparation, Ready for Review, In Review, Approved, Completed, Archived

### Component library

Use **shadcn/ui (New York style)** — this is critical for the right look. Install with:
```bash
npx shadcn@latest init --style new-york
```

Required components:
- `Card` — for all content panels
- `Badge` — for status/type labels (extend with custom color variants)
- `Button` — variants: default (sky-500), secondary (slate-100), outline, ghost
- `Input`, `Textarea` — always with `rounded-lg bg-slate-50`
- `Select` — for dropdown filters
- `Accordion` — for collapsible reasoning/assumptions sections
- `Skeleton` — for loading states (use `rounded-lg`)
- `Sonner` — for toast notifications on mutations
- `Separator` — `border-slate-100`
- `Avatar` — for user display in sidebar
- `Tooltip` — for icon-only buttons
- `Tabs` — for knowledge base category filters
- `Progress` — for confidence scores and suitability
- `Breadcrumb` — for top bar navigation

### Global CSS Requirements

```css
/* globals.css — MANDATORY */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {
  font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

body {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

This ensures NO serif fonts leak through anywhere in the UI.

---

## Demo Flow (what should work end-to-end)

1. Advisor logs in → sees cases dashboard with 2 seeded cases
2. Clicks "Anna Johansson — Retirement Planning" → case detail
3. Sees client info card (Anna, 45, Volvo, ITP1, 57 000 kr/mån, moderate risk)
4. Clicks "Generate Recommendation" → loading state → recommendation appears
5. Reviews reasoning chain (5-7 steps with evidence references)
6. Checks suitability score (8.5/10 gauge)
7. Expands assumptions and scenarios
8. Searches knowledge base for "ITP1 fondval" → sees relevant articles
9. Clicks "Generate Document" → PDF generated
10. Clicks "Download PDF" → downloads recommendation pack
11. Checks audit trail → sees case_created, recommendation_generated, document_generated

This is the core product loop. Everything should feel fast, professional, and trustworthy.

---

## Final Design Checklist

Before outputting, verify:
- [ ] Font is Inter/Geist Sans — NO serif fonts anywhere
- [ ] Sidebar is dark (`bg-slate-950`) with light text
- [ ] Page background is `bg-slate-50`, not pure white
- [ ] All cards use `rounded-xl border border-slate-200/60 shadow-sm`
- [ ] Primary buttons are `bg-sky-500` with `rounded-lg`
- [ ] Badges are `rounded-full text-xs font-medium`
- [ ] All text uses `text-slate-*` color scale
- [ ] Icons are Lucide React, `w-4 h-4`, `text-slate-400` unless active
- [ ] Loading states use shadcn Skeleton with `rounded-lg`
- [ ] The overall feel matches Legora.com / Linear.app / Vercel Dashboard — modern, clean, tech-forward
- [ ] It does NOT look like a basic HTML page or a 2005 website
