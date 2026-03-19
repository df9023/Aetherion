# v0 Prompt 2/3 — Case Detail Page

> **CRITICAL**: Continue using the exact same design system from the previous generation — dark sidebar (`bg-slate-950`), `bg-slate-50` page background, sky-500 accent, Inter font, shadcn/ui New York style, `rounded-xl` cards. This page lives inside that app shell.

## What to build

Build the **Case Detail page** (`/cases/[id]`) — the core workspace where a pension advisor spends most of their time. This page shows case info, client details, an AI recommendation generator, the full recommendation viewer, a knowledge base search panel, and an audit trail.

This is the most important page in the entire product.

---

## Layout

Two-column layout using CSS Grid: `grid grid-cols-[1fr_400px] gap-6`

- **Left column**: Case header, client info, AI recommendation (generate + view)
- **Right column**: Knowledge search panel, audit trail

Wrap in `max-w-7xl mx-auto px-6 py-8`.

---

## Left Column

### Case Header Card

`bg-white rounded-xl border border-slate-200/60 shadow-sm p-6`

- Case title: `text-2xl font-bold tracking-tight text-slate-900`
- Row below title with: Status badge + Case type badge + Meeting date
- "Assigned to: Erik Eriksson" — `text-sm text-slate-500` with `User` icon

### Client Info Card

`bg-white rounded-xl border border-slate-200/60 shadow-sm p-6 mt-4`

Display client details in a clean grid layout (`grid grid-cols-2 gap-4`):
- Client name: `text-lg font-semibold text-slate-900` spanning full width
- Each field as label + value:
  - Label: `text-xs font-medium uppercase tracking-wider text-muted-foreground`
  - Value: `text-sm text-slate-800`
- Fields to show:
  - **Age**: calculated from DOB, e.g. "45 years"
  - **Employer**: "Volvo"
  - **Collective Agreement**: badge `bg-blue-50 text-blue-700 rounded-full text-xs px-2.5 py-0.5` — "ITP1"
  - **Monthly Income**: formatted "57 000 kr/month"
  - **Risk Profile**: badge — Low=`bg-emerald-50 text-emerald-700`, Moderate=`bg-amber-50 text-amber-700`, High=`bg-red-50 text-red-700`
  - **Desired Retirement Age**: "65"
  - **Employment**: "Employed"

### AI Recommendation Section

#### State 1: No recommendation yet

`bg-white rounded-xl border border-slate-200/60 shadow-sm p-8 mt-4`

- Icon: `Sparkles` from Lucide, `w-8 h-8 text-sky-500 mb-3`
- Heading: `text-xl font-semibold text-slate-900` — "AI Recommendation"
- Description: `text-sm text-muted-foreground mt-1 mb-6` — "Generate a structured, evidence-based recommendation powered by AI"
- Optional textarea: shadcn `Textarea` — `bg-slate-50 rounded-lg`, placeholder "Additional context for the AI (optional)..."
- CTA button: `h-12 px-8 bg-sky-500 hover:bg-sky-600 text-white rounded-lg text-sm font-semibold` with `Sparkles` icon. Label: "Generate Recommendation"

#### State 2: Loading (after clicking generate)

Replace the button area with a multi-step progress indicator:
- Three steps shown vertically:
  - `✓ Retrieving knowledge...` (checkmark, `text-emerald-600`)
  - `● Analyzing case...` (pulsing dot animation, `text-sky-500`)
  - `○ Building recommendation...` (gray, waiting)
- Use a subtle shimmer/pulse animation (`animate-pulse`) on the active step
- The whole section should feel alive, not frozen

#### State 3: Recommendation exists

Replace the generate section with the full recommendation viewer:

**Recommendation Header** — `bg-white rounded-xl border border-slate-200/60 shadow-sm p-6 mt-4`:
- Top row `flex items-center justify-between`:
  - Left: `text-xl font-semibold` — "Recommendation v1"
  - Right: Status badge + Type badge
- **Suitability Score** — the most prominent visual element:
  - Large number: `text-4xl font-bold` with `/10` in `text-lg text-muted-foreground`
  - Color: `text-emerald-600` for 8-10, `text-amber-600` for 6-7.9, `text-red-600` for <6
  - Label below: `text-xs uppercase tracking-wider text-muted-foreground` — "Suitability Score"
  - Thin progress bar beneath: shadcn `Progress` component, colored to match score

**Summary** — `mt-6`:
- Label: `text-xs uppercase tracking-wider text-muted-foreground mb-2` — "Summary"
- Text: `text-sm text-slate-700 leading-relaxed`

**Reasoning Chain** — use shadcn `Accordion`, open by default:
- Label: `text-xs uppercase tracking-wider text-muted-foreground mb-3` — "Reasoning"
- Visual stepper layout on the left:
  - Step number: `w-7 h-7 rounded-full bg-sky-50 text-sky-600 text-xs font-bold flex items-center justify-center`
  - Vertical line connecting steps: `border-l-2 border-slate-100`
  - Description: `text-sm text-slate-800 font-medium`
  - Conclusion: `text-sm text-slate-500 mt-1`
  - Evidence badges: small pills `bg-blue-50 text-blue-700 text-xs rounded-full px-2 py-0.5` with `FileText` icon

**Assumptions** — collapsible:
- Label: `text-xs uppercase tracking-wider text-muted-foreground mb-3` — "Assumptions"
- Each: `bg-slate-50 rounded-lg p-4 space-y-2`
  - Assumption: `text-sm font-medium text-slate-800`
  - Basis: `text-xs text-slate-500` prefixed with "Basis:"
  - Impact if wrong: `text-xs text-amber-700 bg-amber-50 rounded-md p-2 mt-2` with `AlertTriangle` icon

**Scenarios** — `grid grid-cols-2 gap-4`:
- Label: `text-xs uppercase tracking-wider text-muted-foreground mb-3` — "Scenarios"
- Each card: `bg-slate-50 rounded-lg p-5 border border-slate-100`
  - Name: `text-sm font-semibold text-slate-800`
  - Description: `text-xs text-slate-500 mt-1`
  - Projected outcome: key-value pairs, keys `font-medium text-slate-600`, values `text-slate-800`, all `text-xs`

**Evidence** — list below scenarios:
- Label: `text-xs uppercase tracking-wider text-muted-foreground mb-3` — "Evidence"
- Each: `bg-white rounded-lg border border-slate-100 p-4`
  - Source type badge: `bg-purple-50 text-purple-700 text-xs rounded-full px-2.5 py-0.5`
  - Source reference: `text-sm font-medium text-slate-800`
  - Content snippet: `text-xs text-slate-500 line-clamp-2` (expandable)
  - Relevance: `text-xs text-slate-400 italic`
  - Confidence: thin progress bar + percentage

**Actions Bar** — `flex items-center gap-3 mt-6 pt-6 border-t border-slate-100`:
- "Generate Document" — `Button` secondary: `bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg h-10 text-sm` with `FileDown` icon
- "Download PDF" — `Button` outline: `border-slate-200 text-slate-700 rounded-lg h-10 text-sm` with `Download` icon
- "Generate New Version" — `Button` ghost: `text-slate-500 hover:text-slate-700 rounded-lg h-10 text-sm` with `RefreshCw` icon, `ml-auto`

---

## Right Column

### Knowledge Search Panel

`bg-white rounded-xl border border-slate-200/60 shadow-sm p-5`

- Title: `text-sm font-semibold text-slate-800 mb-3` — "Knowledge Base"
- Search input: `bg-slate-50 rounded-lg border-slate-200 text-sm h-9` with `Search` icon, placeholder "Search knowledge base..."
- Results: `space-y-2 mt-3`, each:
  - `bg-slate-50 rounded-lg p-3 hover:bg-slate-100 transition-colors cursor-pointer`
  - Title: `text-sm font-medium text-slate-800`
  - Category badge: `text-xs rounded-full px-2 py-0.5 bg-slate-200 text-slate-600`
  - Tags: `text-[10px] bg-sky-50 text-sky-600 rounded-full px-1.5 py-0.5`
  - Expandable content: `text-xs text-slate-600 leading-relaxed mt-2`

### Audit Trail Panel

`bg-white rounded-xl border border-slate-200/60 shadow-sm p-5 mt-4`

- Title: `text-sm font-semibold text-slate-800 mb-3` — "Audit Trail"
- Timeline with vertical line:
  - Line: `border-l-2 border-slate-100 ml-3`
  - Each entry: `flex gap-3 pb-4 relative`
    - Dot: `w-2.5 h-2.5 rounded-full mt-1.5` (green=approvals, blue=generation, gray=others)
    - Action: `text-xs font-medium text-slate-700`
    - Timestamp: `text-[10px] text-slate-400`
    - Actor icon: tiny `User` or `Bot`
- Labels: "Case created", "Recommendation generated by AI", "Document generated", etc.

---

## Mock Data

Use this to populate the page (show State 3 — recommendation exists):

```typescript
const mockCase = {
  id: "case-1",
  title: "Anna Johansson — Retirement Planning",
  case_type: "retirement_planning",
  status: "in_preparation",
  summary: "ITP1 pension review and withdrawal strategy",
  assigned_to: "Erik Eriksson",
  meeting_date: "2026-04-15",
}

const mockClient = {
  name: "Anna Johansson",
  date_of_birth: "1980-03-15",
  employment_status: "employed",
  employer_name: "Volvo",
  collective_agreement: "ITP1",
  annual_income: "684000",
  desired_retirement_age: 65,
  risk_profile: "moderate",
}

const mockRecommendation = {
  id: "rec-1",
  version: 1,
  status: "draft",
  recommendation_type: "withdrawal_plan",
  suitability_score: "8.5",
  summary: "Based on Anna's ITP1 pension through Volvo, moderate risk profile, and desired retirement age of 65, we recommend a phased withdrawal strategy combining her occupational pension with the general pension. The analysis considers current fund allocation, projected returns under multiple scenarios, and tax optimization opportunities through strategic withdrawal timing.",
  reasoning_chain: [
    { step: 1, description: "Analyzed client's current ITP1 pension holdings and projected value at retirement age 65", conclusion: "Current trajectory yields approximately 2.1M SEK in occupational pension at retirement", evidence_ids: ["ev-1"] },
    { step: 2, description: "Evaluated risk profile alignment with current fund allocation", conclusion: "Moderate risk profile is well-matched with current 60/40 equity-bond allocation", evidence_ids: ["ev-2"] },
    { step: 3, description: "Modeled withdrawal scenarios considering tax brackets and general pension coordination", conclusion: "Phased 5-year withdrawal starting at 65 optimizes tax efficiency", evidence_ids: ["ev-3"] },
    { step: 4, description: "Assessed survivor protection needs based on family situation", conclusion: "Current survivor protection level is adequate, no changes recommended", evidence_ids: [] },
    { step: 5, description: "Reviewed applicable product rules and regulatory requirements for ITP1 withdrawals", conclusion: "All recommendations comply with ITP1 product rules and IDD requirements", evidence_ids: ["ev-1", "ev-4"] },
  ],
  assumptions: [
    { assumption: "Client will retire at age 65 as planned", basis: "Client confirmed desired retirement age during advisory meeting", impact_if_wrong: "Earlier retirement would reduce projected pension capital by ~8% per year brought forward" },
    { assumption: "Current employer contributions continue at present level", basis: "Volvo's ITP1 agreement terms and client's employment status", impact_if_wrong: "Job change or salary reduction would lower projected pension by 10-20%" },
    { assumption: "Average annual return of 6% on current fund allocation", basis: "Historical 10-year return for similar moderate-risk portfolios", impact_if_wrong: "A 2% lower return would reduce final capital by approximately 350K SEK" },
  ],
  scenarios: [
    { name: "Base Case", description: "Retirement at 65, current allocation maintained", projected_outcome: { "Monthly pension": "18 500 kr", "Total capital at 65": "2.1M SEK", "Tax rate": "~32%" } },
    { name: "Early Retirement (63)", description: "Retirement 2 years early with reduced capital", projected_outcome: { "Monthly pension": "15 800 kr", "Total capital at 63": "1.8M SEK", "Tax rate": "~30%" } },
    { name: "Optimized Withdrawal", description: "Phased 5-year withdrawal with tax optimization", projected_outcome: { "Monthly pension": "19 200 kr", "Effective tax rate": "~28%", "Tax savings": "~85K SEK" } },
  ],
}

const mockEvidence = [
  { id: "ev-1", source_type: "product_rule", source_reference: "ITP1 Product Rules 2024", content_snippet: "ITP1 pension benefits are calculated based on final salary and years of service. Withdrawal can commence from age 55 with actuarial reduction.", relevance_explanation: "Defines withdrawal rules applicable to client", confidence: "0.95" },
  { id: "ev-2", source_type: "internal_policy", source_reference: "Risk Profile Assessment Playbook", content_snippet: "Moderate risk profile clients should maintain 50-70% equity allocation with gradual de-risking starting 5 years before planned retirement.", relevance_explanation: "Guides fund allocation recommendation", confidence: "0.88" },
  { id: "ev-3", source_type: "regulation", source_reference: "IDD Regulatory Requirements", content_snippet: "Advisors must demonstrate that recommended products and withdrawal strategies are suitable given the client's financial situation, knowledge, and objectives.", relevance_explanation: "Compliance framework for suitability assessment", confidence: "0.92" },
  { id: "ev-4", source_type: "regulation", source_reference: "Pension Withdrawal Rules — Skatteverket", content_snippet: "Occupational pension withdrawals are taxed as employment income. Phased withdrawals over minimum 5 years can optimize tax bracket utilization.", relevance_explanation: "Tax optimization basis for withdrawal timing", confidence: "0.90" },
]

const mockKnowledge = [
  { id: "k-1", title: "ITP1 Product Rules & Fund Selection", category: "product_rule", tags: ["ITP1", "funds", "withdrawal"], content: "ITP1 is a defined-contribution plan where the employer pays premiums..." },
  { id: "k-2", title: "ITP2 Traditional & ITPK Rules", category: "product_rule", tags: ["ITP2", "traditional", "ITPK"], content: "ITP2 consists of a defined-benefit base and ITPK supplementary..." },
  { id: "k-3", title: "Löneväxling Internal Policy", category: "internal_policy", tags: ["salary exchange", "policy"], content: "Salary exchange (löneväxling) allows employees to convert..." },
]

const mockAudit = [
  { action: "case_created", actor_type: "user", timestamp: "2026-03-16T09:00:00Z" },
  { action: "recommendation_generated", actor_type: "system", timestamp: "2026-03-16T09:15:00Z" },
]
```

---

## API Contracts (for reference — use mock data for now)

```typescript
// POST /api/v1/cases/{case_id}/generate-recommendation
// Body: { additional_context?: string }

interface RecommendationResponse {
  id: string; case_id: string; version: number;
  recommendation_type: string; status: string;
  summary: string; suitability_score: string | null;
  reasoning_chain: { step: number; description: string; evidence_ids: string[]; conclusion: string }[];
  assumptions: { assumption: string; basis: string; impact_if_wrong: string }[];
  scenarios: { name: string; description: string; projected_outcome: Record<string, any> }[] | null;
  created_at: string; created_by: string; approved_by: string | null;
}

// POST /api/v1/knowledge/search → KnowledgeItemResponse[]
// GET /api/v1/cases/{case_id}/audit → AuditEntryResponse[]
// POST /api/v1/recommendations/{id}/generate-document → DocumentResponse
// GET /api/v1/documents/{id}/download → file
```

---

## Design Checklist

- [ ] Uses the same design system as the app shell/dashboard (dark sidebar, slate-50 background, sky-500 accent)
- [ ] Two-column grid layout — not a single column
- [ ] Suitability score is visually prominent (large number, colored)
- [ ] Reasoning chain has a stepper/timeline visual, not just a flat list
- [ ] Assumptions show impact-if-wrong in amber warning style
- [ ] All cards are `rounded-xl` with `shadow-sm`
- [ ] Font is Inter — NO serif fonts
- [ ] Feels like Legora / Linear — premium, tech-forward, not a template
