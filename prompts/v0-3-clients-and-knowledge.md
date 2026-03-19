# v0 Prompt 3/3 — Clients & Knowledge Base Pages

> **CRITICAL**: Continue using the exact same design system from the previous generations — dark sidebar (`bg-slate-950`), `bg-slate-50` page background, sky-500 accent, Inter font, shadcn/ui New York style, `rounded-xl` cards. These pages live inside the same app shell.

## What to build

Build two simple pages that follow the same visual patterns established in the Cases Dashboard:

1. **Clients page** (`/clients`) — grid of client cards
2. **Knowledge Base page** (`/knowledge`) — searchable/filterable list of institutional knowledge articles

Both are inside the existing app shell (dark sidebar + top bar).

---

## Page 1: Clients (`/clients`)

Wrap in `max-w-7xl mx-auto px-6 py-8`.

**Header** — `flex items-center justify-between mb-8`:
- Left:
  - Title: `text-3xl font-bold tracking-tight text-slate-900` — "Clients"
  - Subtitle: `text-sm text-muted-foreground mt-1` — "Manage client profiles and information"
- Right: `Button` accent — `bg-sky-500 hover:bg-sky-600 text-white rounded-lg h-10 px-4 text-sm font-medium` with `Plus` icon. Label: "New Client"

**Search** — `mb-6`:
- Input: `w-80 bg-white rounded-lg border-slate-200` with `Search` icon, placeholder "Search clients..."

**Client cards** — `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4`:

Each card: `bg-white rounded-xl border border-slate-200/60 shadow-sm p-5 hover:shadow-md hover:border-slate-300 transition-all duration-200 cursor-pointer`

Layout inside card:
- Top row: Name + Age
  - Name: `text-base font-semibold text-slate-900`
  - Age: `text-sm text-slate-400 ml-2` — e.g. "45 years"
- Middle: `mt-3 space-y-2`
  - Employer + Agreement: `text-sm text-slate-600` — "Volvo" + badge `bg-blue-50 text-blue-700 text-xs rounded-full px-2.5 py-0.5 ml-2` — "ITP1"
  - Income: `text-sm text-slate-500` — "57 000 kr/month"
- Bottom: `mt-3 flex items-center gap-2`
  - Risk profile badge:
    - Low: `bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs rounded-full px-2.5 py-0.5`
    - Moderate: `bg-amber-50 text-amber-700 border border-amber-200 text-xs rounded-full px-2.5 py-0.5`
    - High: `bg-red-50 text-red-700 border border-red-200 text-xs rounded-full px-2.5 py-0.5`
  - Employment status: `text-xs text-slate-400`

### Mock Data

```typescript
const mockClients = [
  {
    id: "client-1",
    name: "Anna Johansson",
    date_of_birth: "1980-03-15",
    employer_name: "Volvo",
    collective_agreement: "ITP1",
    annual_income: "684000",
    risk_profile: "moderate",
    employment_status: "employed",
    desired_retirement_age: 65,
  },
  {
    id: "client-2",
    name: "Lars Pettersson",
    date_of_birth: "1968-07-22",
    employer_name: "Ericsson",
    collective_agreement: "ITP2",
    annual_income: "960000",
    risk_profile: "low",
    employment_status: "employed",
    desired_retirement_age: 63,
  },
]
```

---

## Page 2: Knowledge Base (`/knowledge`)

Wrap in `max-w-7xl mx-auto px-6 py-8`.

**Header** — `mb-8`:
- Title: `text-3xl font-bold tracking-tight text-slate-900` — "Knowledge Base"
- Subtitle: `text-sm text-muted-foreground mt-1` — "Institutional knowledge, product rules, and regulatory content"

**Search & Filters** — `mb-6`:
- Large search input: `w-full max-w-xl bg-white rounded-lg border-slate-200 h-12 text-sm` with `Search` icon, placeholder "Search knowledge..."
- Category filter below: shadcn `Tabs` with `TabsList` — `bg-slate-100 rounded-lg p-1 mt-4`:
  - Tab items: `text-xs font-medium rounded-md px-3 py-1.5`
  - Tabs: All, Product Rules, Internal Policy, Regulatory, Playbook, Precedent, FAQ, Process Guide
  - Active tab: `bg-white shadow-sm text-slate-900`
  - Inactive: `text-slate-500 hover:text-slate-700`

**Knowledge items** — `space-y-3`:

Each: `bg-white rounded-xl border border-slate-200/60 shadow-sm p-5 hover:shadow-md hover:border-slate-300 transition-all duration-200`

- Top row: `flex items-center justify-between`
  - Title: `text-sm font-semibold text-slate-800`
  - Category badge (color by category):
    - Product Rules: `bg-blue-50 text-blue-700`
    - Internal Policy: `bg-violet-50 text-violet-700`
    - Regulatory: `bg-amber-50 text-amber-700`
    - Playbook: `bg-emerald-50 text-emerald-700`
    - Precedent: `bg-slate-100 text-slate-600`
    - FAQ: `bg-sky-50 text-sky-700`
    - Process Guide: `bg-rose-50 text-rose-700`
  - All badges: `text-xs rounded-full px-2.5 py-0.5 font-medium`
- Source: `text-xs text-slate-400 mt-1` — with `FileText` icon `w-3 h-3 inline mr-1`
- Tags: `flex gap-1.5 mt-2 flex-wrap`, each tag `text-[10px] bg-sky-50 text-sky-600 rounded-full px-2 py-0.5 font-medium`
- Content excerpt: `text-xs text-slate-500 mt-3 line-clamp-3 leading-relaxed`
- "Show more" toggle: `text-xs text-sky-500 hover:text-sky-600 font-medium cursor-pointer mt-2` — expands to show full content

### Mock Data

```typescript
const mockKnowledge = [
  {
    id: "k-1",
    title: "ITP1 Product Rules & Fund Selection",
    category: "product_rule",
    source: "Collectum Product Guide 2024",
    tags: ["ITP1", "funds", "withdrawal", "collectum"],
    content: "ITP1 is a defined-contribution occupational pension plan managed through Collectum. The employee selects fund allocation from approved providers. Key withdrawal rules: benefits can be drawn from age 55 with actuarial reduction, standard retirement age is 65. Fund selection options include traditional insurance and unit-linked (fondförsäkring). Transfer rights exist between approved providers with restrictions on traditional insurance policies. Maximum fund fee caps apply per Collectum's agreement.",
    effective_date: "2024-01-01",
    is_active: true,
  },
  {
    id: "k-2",
    title: "ITP2 Traditional & ITPK Rules",
    category: "product_rule",
    source: "Alecta/Collectum Handbook",
    tags: ["ITP2", "traditional", "ITPK", "defined-benefit"],
    content: "ITP2 consists of a defined-benefit base pension (managed by Alecta) and a supplementary ITPK component (employee-directed). The DB base provides approximately 10% of salary between 7.5-20 income base amounts and 65% between 20-30 IBB. ITPK premiums are 2% of pensionable salary. ITPK can be placed in traditional insurance or unit-linked alternatives. Important: the DB component cannot be transferred and follows Alecta's terms.",
    effective_date: "2024-01-01",
    is_active: true,
  },
  {
    id: "k-3",
    title: "Löneväxling Internal Policy",
    category: "internal_policy",
    source: "NordPension Advisory Handbook",
    tags: ["salary exchange", "löneväxling", "policy", "guidelines"],
    content: "Salary exchange (löneväxling) allows employees to convert gross salary into additional pension contributions. Our advisory guidelines: minimum income threshold of 40,000 kr/month before recommending löneväxling, always assess impact on sjukpenning/föräldrapenning, consider social security ceiling (10 IBB), document client understanding of trade-offs. For ITP2 clients, coordinate with existing DB benefits to avoid over-insurance.",
    effective_date: "2023-06-15",
    is_active: true,
  },
  {
    id: "k-4",
    title: "IDD Regulatory Requirements",
    category: "regulatory_requirement",
    source: "Finansinspektionen FFFS 2018:10",
    tags: ["IDD", "compliance", "suitability", "disclosure"],
    content: "The Insurance Distribution Directive (IDD) requires advisors to: conduct a demands-and-needs analysis, assess suitability based on client's knowledge, financial situation, and objectives, disclose all costs and fees in standardized format, identify and manage conflicts of interest, provide recommendations in writing with clear justification. Non-compliance may result in sanctions from Finansinspektionen.",
    effective_date: "2018-10-01",
    is_active: true,
  },
  {
    id: "k-5",
    title: "Risk Profile Assessment Playbook",
    category: "playbook",
    source: "NordPension Internal",
    tags: ["risk", "assessment", "methodology"],
    content: "Risk profiling methodology: Use structured questionnaire covering investment horizon, loss tolerance, income stability, and experience. Map to three-tier scale (Low/Moderate/High). Low: max 30% equity, capital preservation priority. Moderate: 40-70% equity, balanced growth. High: 70%+ equity, growth-oriented. Review risk profile annually and at major life events. Document any deviation from recommended allocation with client acknowledgment.",
    effective_date: "2023-01-01",
    is_active: true,
  },
  {
    id: "k-6",
    title: "Pension Withdrawal Rules & Tax Optimization",
    category: "regulatory_requirement",
    source: "Skatteverket Guidelines",
    tags: ["withdrawal", "tax", "optimization", "pension age"],
    content: "Occupational pension can generally be withdrawn from age 55 (moving to 56 in 2026). General pension (allmän pension) available from 63 (moving to 64 in 2026). Withdrawals taxed as employment income (PAYG). Key optimization: phased withdrawals over 5+ years can reduce marginal tax rate by keeping annual income below municipal tax ceiling. Coordinate occupational and general pension withdrawal timing. Consider impact on housing allowance and other means-tested benefits for low-income retirees.",
    effective_date: "2024-01-01",
    is_active: true,
  },
]
```

---

## Technical Details

- These pages live inside the same app shell layout from Prompt 1
- Use shadcn/ui (New York style): `Card`, `Badge`, `Button`, `Input`, `Tabs`, `TabsList`, `TabsTrigger`, `Skeleton`
- Use Lucide icons
- All text in English; Swedish terms in data stay as-is
- Use mock data for now (will be replaced with API calls later)

---

## Design Checklist

- [ ] Same design system as previous pages — consistent look
- [ ] Client cards in responsive grid (1/2/3 columns)
- [ ] Knowledge items have colored category badges
- [ ] Category tabs use shadcn Tabs with subtle active state
- [ ] Content excerpts are truncated with "Show more"
- [ ] Tags are tiny pills with sky-50 background
- [ ] All cards `rounded-xl`, `shadow-sm`, proper hover states
- [ ] Font is Inter — NO serif fonts
- [ ] Feels like a continuation of the same premium product
