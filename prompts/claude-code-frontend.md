# Claude Code Prompt — Scaffold Aetherion Frontend

## Goal

Scaffold a complete Next.js 14 frontend in `frontend/` for the Aetherion Workbench — a pension advisory workspace. The backend API already exists at `http://localhost:8000/api/v1`. Use mock data for now; we'll wire up real API calls later.

**If you run low on context, stop after completing the App Shell + Cases Dashboard. The case detail page is the second priority.**

---

## Step 1: Project Setup

```bash
cd /home/daniel/projects/Aetherion
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*" --use-npm
cd frontend
```

Install dependencies:
```bash
npx shadcn@latest init --style new-york --base-color slate --css-variables --tailwind-css app/globals.css --tailwind-config tailwind.config.ts --components-path @/components --utils-path @/lib/utils --rsc
npm install @tanstack/react-query lucide-react
```

Add shadcn components:
```bash
npx shadcn@latest add card badge button input textarea select accordion skeleton separator avatar tooltip tabs progress breadcrumb sonner
```

---

## Step 2: Design System

### `app/globals.css`

Replace the default globals.css with:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 210 40% 98%;       /* slate-50 */
    --foreground: 222 47% 11%;       /* slate-900 */
    --card: 0 0% 100%;
    --card-foreground: 222 47% 11%;
    --popover: 0 0% 100%;
    --popover-foreground: 222 47% 11%;
    --primary: 199 89% 48%;           /* sky-500 */
    --primary-foreground: 0 0% 100%;
    --secondary: 210 40% 96%;         /* slate-100 */
    --secondary-foreground: 222 47% 11%;
    --muted: 210 40% 96%;
    --muted-foreground: 215 16% 47%;  /* slate-500 */
    --accent: 210 40% 96%;
    --accent-foreground: 222 47% 11%;
    --destructive: 0 84% 60%;
    --destructive-foreground: 0 0% 100%;
    --border: 214 32% 91%;            /* slate-200 */
    --input: 214 32% 91%;
    --ring: 199 89% 48%;
    --radius: 0.75rem;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground antialiased;
  }
}
```

### `app/layout.tsx`

```tsx
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Aetherion — Workbench",
  description: "AI-native decision workspace for pension advisory",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.className} antialiased`}>
        {children}
      </body>
    </html>
  )
}
```

---

## Step 3: App Shell

Create a layout with a fixed dark sidebar + sticky top bar. All page content renders in the main area.

### Sidebar (`components/sidebar.tsx`)

- Fixed left, `w-64`, full height, `bg-slate-950`
- Top: "Aetherion" wordmark — `text-lg font-bold text-white` with a small diamond/gem unicode character ◆
- Separator: `border-slate-800`
- Nav items (use Next.js `Link` + `usePathname` for active state):
  - Cases — `Briefcase` icon — `/cases`
  - Clients — `Users` icon — `/clients`
  - Knowledge Base — `BookOpen` icon — `/knowledge`
- Active nav item: `bg-sky-500/10 text-sky-400 border-l-2 border-sky-400`
- Inactive: `text-slate-400 hover:bg-slate-800/50 hover:text-slate-100`
- Each nav item: `px-4 py-2.5 flex items-center gap-3 text-sm font-medium rounded-r-lg`
- Bottom (mt-auto): Avatar + "Erik Eriksson" + "Advisor" badge + Settings gear icon

### Top Bar (`components/top-bar.tsx`)

- `sticky top-0 z-10 h-14 bg-white/80 backdrop-blur-sm border-b border-slate-200/60`
- Left: Breadcrumb (use shadcn Breadcrumb) — dynamic based on route
- Right: Org badge "NordPension Rådgivning AB" — `text-xs font-medium text-slate-500 bg-slate-100 px-3 py-1 rounded-full`

### App Layout (`app/(dashboard)/layout.tsx`)

Use a route group `(dashboard)` so all pages share the shell:

```
app/
  (dashboard)/
    layout.tsx        → Sidebar + TopBar + main content area
    cases/
      page.tsx        → Cases dashboard
      [id]/
        page.tsx      → Case detail
    clients/
      page.tsx
    knowledge/
      page.tsx
  layout.tsx          → Root layout (font, html)
  page.tsx            → Redirect to /cases
```

The dashboard layout renders:
- Sidebar (fixed)
- Main area (`ml-64 min-h-screen bg-slate-50`) with TopBar + `{children}` wrapped in `max-w-7xl mx-auto px-6 py-8`

---

## Step 4: Mock Data

Create `lib/mock-data.ts` with all mock data. This file is the single source of truth until we wire up the API.

```typescript
export const mockUsers = {
  "user-1": { id: "user-1", name: "Erik Eriksson", role: "advisor" },
  "user-2": { id: "user-2", name: "Maria Lindqvist", role: "advisor" },
}

export const mockClients = [
  {
    id: "client-1",
    name: "Anna Johansson",
    date_of_birth: "1980-03-15",
    employment_status: "employed" as const,
    employer_name: "Volvo",
    collective_agreement: "ITP1",
    annual_income: "684000",
    desired_retirement_age: 65,
    risk_profile: "moderate" as const,
    organization_id: "org-1",
    created_at: "2026-03-10T08:00:00Z",
    updated_at: "2026-03-10T08:00:00Z",
    created_by: "user-1",
  },
  {
    id: "client-2",
    name: "Lars Pettersson",
    date_of_birth: "1968-07-22",
    employment_status: "employed" as const,
    employer_name: "Ericsson",
    collective_agreement: "ITP2",
    annual_income: "960000",
    desired_retirement_age: 63,
    risk_profile: "low" as const,
    organization_id: "org-1",
    created_at: "2026-03-10T08:00:00Z",
    updated_at: "2026-03-10T08:00:00Z",
    created_by: "user-2",
  },
]

export const mockCases = [
  {
    id: "case-1",
    title: "Anna Johansson — Retirement Planning",
    case_type: "retirement_planning" as const,
    status: "in_preparation" as const,
    summary: "ITP1 pension review and withdrawal strategy for client approaching retirement",
    meeting_date: "2026-04-15T10:00:00Z",
    client_id: "client-1",
    assigned_to: "user-1",
    organization_id: "org-1",
    created_at: new Date(Date.now() - 2 * 86400000).toISOString(),
    updated_at: new Date().toISOString(),
    completed_at: null,
  },
  {
    id: "case-2",
    title: "Lars Pettersson — Salary Exchange",
    case_type: "salary_exchange" as const,
    status: "draft" as const,
    summary: "Löneväxling analysis for ITP2 client at Ericsson",
    meeting_date: null,
    client_id: "client-2",
    assigned_to: "user-2",
    organization_id: "org-1",
    created_at: new Date(Date.now() - 5 * 86400000).toISOString(),
    updated_at: new Date().toISOString(),
    completed_at: null,
  },
]

export const mockRecommendation = {
  id: "rec-1",
  case_id: "case-1",
  version: 1,
  status: "draft" as const,
  recommendation_type: "withdrawal_plan" as const,
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
  created_at: "2026-03-16T09:15:00Z",
  created_by: "user-1",
  approved_by: null,
}

export const mockEvidence = [
  { id: "ev-1", recommendation_id: "rec-1", source_type: "product_rule" as const, source_reference: "ITP1 Product Rules 2024", content_snippet: "ITP1 pension benefits are calculated based on final salary and years of service. Withdrawal can commence from age 55 with actuarial reduction.", relevance_explanation: "Defines withdrawal rules applicable to client", confidence: "0.95", created_at: "2026-03-16T09:15:00Z" },
  { id: "ev-2", recommendation_id: "rec-1", source_type: "internal_policy" as const, source_reference: "Risk Profile Assessment Playbook", content_snippet: "Moderate risk profile clients should maintain 50-70% equity allocation with gradual de-risking starting 5 years before planned retirement.", relevance_explanation: "Guides fund allocation recommendation", confidence: "0.88", created_at: "2026-03-16T09:15:00Z" },
  { id: "ev-3", recommendation_id: "rec-1", source_type: "regulation" as const, source_reference: "IDD Regulatory Requirements", content_snippet: "Advisors must demonstrate that recommended products and withdrawal strategies are suitable given the client's financial situation, knowledge, and objectives.", relevance_explanation: "Compliance framework for suitability assessment", confidence: "0.92", created_at: "2026-03-16T09:15:00Z" },
  { id: "ev-4", recommendation_id: "rec-1", source_type: "regulation" as const, source_reference: "Pension Withdrawal Rules — Skatteverket", content_snippet: "Occupational pension withdrawals are taxed as employment income. Phased withdrawals over minimum 5 years can optimize tax bracket utilization.", relevance_explanation: "Tax optimization basis for withdrawal timing", confidence: "0.90", created_at: "2026-03-16T09:15:00Z" },
]

export const mockKnowledge = [
  { id: "k-1", title: "ITP1 Product Rules & Fund Selection", category: "product_rule" as const, source: "Collectum Product Guide 2024", tags: ["ITP1", "funds", "withdrawal", "collectum"], content: "ITP1 is a defined-contribution occupational pension plan managed through Collectum. The employee selects fund allocation from approved providers. Key withdrawal rules: benefits can be drawn from age 55 with actuarial reduction, standard retirement age is 65. Fund selection options include traditional insurance and unit-linked (fondförsäkring). Transfer rights exist between approved providers with restrictions on traditional insurance policies.", effective_date: "2024-01-01", is_active: true },
  { id: "k-2", title: "ITP2 Traditional & ITPK Rules", category: "product_rule" as const, source: "Alecta/Collectum Handbook", tags: ["ITP2", "traditional", "ITPK", "defined-benefit"], content: "ITP2 consists of a defined-benefit base pension (managed by Alecta) and a supplementary ITPK component (employee-directed). The DB base provides approximately 10% of salary between 7.5-20 income base amounts and 65% between 20-30 IBB. ITPK premiums are 2% of pensionable salary.", effective_date: "2024-01-01", is_active: true },
  { id: "k-3", title: "Löneväxling Internal Policy", category: "internal_policy" as const, source: "NordPension Advisory Handbook", tags: ["salary exchange", "löneväxling", "policy"], content: "Salary exchange (löneväxling) allows employees to convert gross salary into additional pension contributions. Our advisory guidelines: minimum income threshold of 40,000 kr/month before recommending löneväxling, always assess impact on sjukpenning/föräldrapenning.", effective_date: "2023-06-15", is_active: true },
  { id: "k-4", title: "IDD Regulatory Requirements", category: "regulatory_requirement" as const, source: "Finansinspektionen FFFS 2018:10", tags: ["IDD", "compliance", "suitability"], content: "The Insurance Distribution Directive (IDD) requires advisors to: conduct a demands-and-needs analysis, assess suitability based on client's knowledge, financial situation, and objectives, disclose all costs and fees in standardized format, identify and manage conflicts of interest.", effective_date: "2018-10-01", is_active: true },
  { id: "k-5", title: "Risk Profile Assessment Playbook", category: "playbook" as const, source: "NordPension Internal", tags: ["risk", "assessment", "methodology"], content: "Risk profiling methodology: Use structured questionnaire covering investment horizon, loss tolerance, income stability, and experience. Map to three-tier scale (Low/Moderate/High). Review risk profile annually and at major life events.", effective_date: "2023-01-01", is_active: true },
  { id: "k-6", title: "Pension Withdrawal Rules & Tax Optimization", category: "regulatory_requirement" as const, source: "Skatteverket Guidelines", tags: ["withdrawal", "tax", "optimization"], content: "Occupational pension can generally be withdrawn from age 55. General pension available from age 63. Withdrawals taxed as employment income. Key optimization: phased withdrawals over 5+ years can reduce marginal tax rate.", effective_date: "2024-01-01", is_active: true },
]

export const mockAudit = [
  { id: "a-1", case_id: "case-1", action: "case_created", actor_id: "user-1", actor_type: "user" as const, details: { case_type: "retirement_planning" }, timestamp: "2026-03-16T09:00:00Z" },
  { id: "a-2", case_id: "case-1", action: "recommendation_generated", actor_id: "system", actor_type: "system" as const, details: { version: 1, recommendation_type: "withdrawal_plan" }, timestamp: "2026-03-16T09:15:00Z" },
]
```

---

## Step 5: Pages

### Cases Dashboard (`app/(dashboard)/cases/page.tsx`)

- Header: "Cases" title + "New Case" button
- Filters: Search input + Status select + Case type select
- Case cards in `space-y-3` — each card clickable, navigates to `/cases/[id]`
- Card layout: title, type badge, status badge (color-coded), relative date, assigned advisor
- Use the mock data directly (no API call yet)

Status badge colors:
- draft → `bg-slate-100 text-slate-600`
- in_preparation → `bg-blue-50 text-blue-700 border border-blue-200`
- ready_for_review → `bg-amber-50 text-amber-700 border border-amber-200`
- in_review → `bg-purple-50 text-purple-700 border border-purple-200`
- approved → `bg-emerald-50 text-emerald-700 border border-emerald-200`
- completed → `bg-green-50 text-green-800 border border-green-200`
- archived → `bg-slate-50 text-slate-400`

Case type display names: pension_review → "Pension Review", retirement_planning → "Retirement Planning", salary_exchange → "Salary Exchange", transfer_advice → "Transfer Advice", survivor_protection → "Survivor Protection", decumulation → "Decumulation", other → "Other"

### Case Detail (`app/(dashboard)/cases/[id]/page.tsx`)

Two-column grid: `grid grid-cols-[1fr_400px] gap-6`

**Left column** (top to bottom):

1. **Case header card** — title, status badge, type badge, meeting date, assigned advisor
2. **Client info card** — grid of client fields (name, age, employer, agreement badge, monthly income formatted, risk profile badge, retirement age, employment status)
3. **AI Recommendation section** — three states:
   - **Empty state**: Sparkles icon, "AI Recommendation" heading, textarea for optional context, "Generate Recommendation" button (sky-500, h-12)
   - **Loading state**: Three-step progress (Retrieving knowledge → Analyzing case → Building recommendation) with pulse animation. Simulate with a setTimeout toggle.
   - **Recommendation view**: Show the full mockRecommendation data:
     - Suitability score: large `text-4xl font-bold` number with color coding + progress bar
     - Summary paragraph
     - Reasoning chain: stepper with numbered circles, vertical connecting line, description + conclusion for each step, evidence badges
     - Assumptions: cards with amber impact-if-wrong warnings
     - Scenarios: 2-column grid of scenario cards with projected outcome key-value pairs
     - Evidence: list with source type badges, snippets, confidence bars
     - Actions bar: Generate Document, Download PDF, Generate New Version buttons

   **Default the page to showing State 3 (recommendation exists)** so we can see how it looks with data.

**Right column**:

1. **Knowledge search panel** — search input + list of knowledge items (from mockKnowledge). Each shows title, category badge, tags. Clicking expands content.
2. **Audit trail panel** — timeline with dots + vertical line. Show mockAudit entries with action labels ("Case created", "Recommendation generated by AI"), timestamps, actor type icons.

### Clients Page (`app/(dashboard)/clients/page.tsx`)

- Header: "Clients" title + "New Client" button
- Search input
- Grid of client cards: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4`
- Each card: name, age (calculated), employer + agreement badge, income formatted, risk profile badge

### Knowledge Base Page (`app/(dashboard)/knowledge/page.tsx`)

- Header: "Knowledge Base" title
- Search input (full width, max-w-xl)
- Category tabs using shadcn Tabs: All, Product Rules, Internal Policy, Regulatory, Playbook, Precedent, FAQ, Process Guide
- Knowledge items: title, colored category badge, source, tags as tiny pills, content excerpt (line-clamp-3), "Show more" toggle

Category badge colors:
- product_rule → `bg-blue-50 text-blue-700`
- internal_policy → `bg-violet-50 text-violet-700`
- regulatory_requirement → `bg-amber-50 text-amber-700`
- playbook → `bg-emerald-50 text-emerald-700`
- precedent → `bg-slate-100 text-slate-600`
- faq → `bg-sky-50 text-sky-700`
- process_guide → `bg-rose-50 text-rose-700`

---

## Step 6: Root page redirect

`app/page.tsx` should redirect to `/cases`:

```tsx
import { redirect } from "next/navigation"
export default function Home() { redirect("/cases") }
```

---

## Design Rules (MANDATORY)

- Font: Inter via next/font. NEVER serif.
- Sidebar: `bg-slate-950`, active item `text-sky-400`
- Page bg: `bg-slate-50`
- All cards: `bg-white rounded-xl border border-slate-200/60 shadow-sm`
- Card hover: `hover:shadow-md hover:border-slate-300 transition-all duration-200`
- Primary buttons: `bg-sky-500 hover:bg-sky-600 text-white rounded-lg`
- Badges: `rounded-full text-xs font-medium px-2.5 py-0.5`
- Section labels: `text-xs font-medium uppercase tracking-wider text-muted-foreground`
- Icons: Lucide React, `w-4 h-4`, `text-slate-400` unless active
- All UI text: English. Swedish terms in data (ITP1, org names) stay as-is.

---

## Verify

After building, run `npm run dev` and confirm:
1. Sidebar is dark with sky accent active state
2. Cases dashboard shows 2 case cards
3. Clicking a case shows the detail page with recommendation
4. Client page shows 2 client cards
5. Knowledge page shows 6 knowledge items with category tabs
6. No serif fonts anywhere
7. It looks like a premium SaaS product (Linear / Vercel Dashboard aesthetic)
