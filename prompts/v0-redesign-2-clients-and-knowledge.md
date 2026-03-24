# Aetherion — Part 2: Clients List, Client Detail, Knowledge Base

This is Part 2 of the Aetherion frontend prototype. **Part 1 already built the App Shell (sidebar + top bar) and Cases pages.** This prompt adds the remaining three pages to the same project. Keep the exact same design system.

Use **shadcn/ui** (New York style), **Tailwind CSS**, **Inter** font, **Lucide React** icons.

## DESIGN RULES (same as Part 1)

- **Sidebar**: `bg-slate-950`. Active nav: `text-sky-400 bg-sky-500/10 border-l-2 border-sky-400`.
- **Content area**: `bg-slate-50`. Cards: `bg-white border border-slate-200/60 shadow-sm rounded-xl`.
- **Text**: `text-slate-900` headings, `text-slate-600` body, `text-slate-400` metadata.
- **Buttons**: Primary `bg-sky-500 hover:bg-sky-600 text-white rounded-lg`. Secondary `border border-slate-200 bg-white text-slate-700 rounded-lg`.
- **Badges**: `rounded-full px-2.5 py-0.5 text-xs font-medium` with semantic colors (emerald success, amber warning, red error).
- **Section headers**: `text-xs font-medium uppercase tracking-wider text-slate-400`.
- **List hover**: `border-l-4 border-transparent` → `border-l-4 border-sky-400 transition-all duration-200`.
- **No**: serif fonts, gradients, colored card backgrounds, decorative illustrations.

---

## CLIENTS LIST (`/clients`)

### Page header
"Clients" in `text-2xl font-semibold text-slate-900` + "New Client" button (`bg-sky-500`, `Plus` icon).

### Search
Full-width input with `Search` icon, `placeholder="Search clients..."`.

### Client cards (grid, `grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4`)

Each card (`rounded-xl border border-slate-200/60 bg-white shadow-sm p-5`):
- Initials avatar: `h-10 w-10 rounded-full bg-slate-100 text-sm font-medium text-slate-600` (centered initials)
- Name: `text-sm font-semibold text-slate-900` — e.g., "Anna Johansson"
- Age: `text-xs text-slate-400` — e.g., "45 years"
- Employer row: `Building2` icon + employer name in `text-sm text-slate-600`
- Income row: `text-sm text-slate-600` — formatted like "57 000 kr/month"
- Risk profile badge with `Shield` icon:
  - Low: `bg-emerald-50 text-emerald-700`
  - Moderate: `bg-amber-50 text-amber-700`
  - High: `bg-red-50 text-red-700`
- Hover: `border-l-4 border-sky-400`

Cards link to `/clients/[id]`.

### Empty state
`Users` icon `h-12 w-12 text-slate-300` centered. "No clients found" + "Create your first client to get started" + "New Client" button.

### Create Client dialog (triggered by "New Client" button)
shadcn/ui `Dialog` (`max-w-2xl`). Title: "New Client". Two-column form (`grid grid-cols-2 gap-4`):
- **First Name** + **Last Name**: `Input`, required.
- **Date of Birth**: `Input` (date), required.
- **Employer**: `Input`, placeholder "e.g., Volvo Group AB".
- **Collective Agreement**: `Select` — ITP1, ITP2, SAF-LO, KAP-KL, PA 16, Other.
- **Annual Income**: `Input` (number), placeholder "e.g., 684000".
- **Employment Status**: `Select` — Employed, Self-employed, Retired, Unemployed.
- **Risk Profile**: `Select` — Low, Moderate, High.
- **Desired Retirement Age**: `Input` (number).

Footer: "Cancel" (outline) + "Create Client" (sky-500). Show this dialog in the open state.

---

## CLIENT DETAIL (`/clients/[id]`)

### Client header card
- Large initials avatar (`h-14 w-14 rounded-full bg-slate-100 text-lg font-semibold text-slate-600`)
- Name: `text-xl font-semibold text-slate-900` — "Anna Johansson"
- Below name: Date of birth + age (`text-sm text-slate-500` — "Born 1981-03-15 · 45 years")
- Employment status badge: `bg-emerald-50 text-emerald-700 rounded-full px-2.5 py-0.5 text-xs font-medium` — "Employed"

### Details card
- Section header: "DETAILS" (`text-xs font-medium uppercase tracking-wider text-slate-400`)
- Two-column grid (`grid grid-cols-2 gap-4`):
  - **Employer**: Volvo Group AB
  - **Collective Agreement**: ITP1 (in blue badge `bg-blue-50 text-blue-700`)
  - **Annual Income**: 684 000 kr
  - **Monthly Income**: 57 000 kr
  - **Desired Retirement Age**: 65
  - **Risk Profile**: Moderate (amber badge)
  - **Employment Status**: Employed

### Document Ingestion card (KEY FEATURE)
Header: `Upload` icon + "Document Ingestion" in `text-base font-semibold`.

**State 1 — Upload**:
- Dashed border dropzone: `border-2 border-dashed border-slate-300 rounded-xl p-8`
- `Upload` icon `h-10 w-10 text-slate-300` centered
- "Upload pension document" in `text-sm font-medium text-slate-700`
- "Drop a PDF here or click to browse" in `text-xs text-slate-400`
- Below: "Supported formats: PDF. Max size 10 MB." in `text-xs text-slate-400`

**State 2 — Extracting** (show this state):
- 3 progress steps in vertical list:
  1. "Extracting text from document..." — completed (green check)
  2. "Analyzing pension data..." — in progress (spinning indicator)
  3. "Building structured output..." — pending (gray circle)
- Animated pulse on the active step
- "This may take 15-30 seconds" in `text-xs text-slate-400`

**State 3 — Review** (show this state as default):
- "Review Extracted Data" heading
- Two-column grid of extracted fields. Each field row:
  - Checkbox (checked by default)
  - Field name: `text-xs text-slate-400 uppercase tracking-wider` — e.g., "COLLECTIVE AGREEMENT"
  - Extracted value: `text-sm font-medium text-slate-900` — e.g., "ITP1"
  - Confidence indicator:
    - ≥80%: `CheckCircle` icon green-500 + `text-xs text-green-600` "98%"
    - 50-80%: `AlertTriangle` icon amber-500 + `text-xs text-amber-600` "72%"
    - <50%: `AlertCircle` icon red-500 + `text-xs text-red-600` "35%"
  - If value differs from current: show `current → extracted` with `ArrowRight` icon in slate-400

Example extracted fields:
| Field | Value | Confidence | Current |
|-------|-------|------------|---------|
| Employer | Volvo Group AB | 98% ✓ | Same |
| Collective Agreement | ITP1 | 95% ✓ | Same |
| Pension Provider | Collectum | 88% ✓ | Not set → Collectum |
| Annual Income | 720 000 kr | 72% ⚠ | 684 000 kr → 720 000 kr |
| Survivor Protection | Yes, 5 years | 65% ⚠ | Not set → Yes |
| Risk Profile | Moderate | 42% ⚠ | Same |

**Fund Allocations** (below fields, if extracted):
Small table with 3 columns: Fund Name, Allocation %, Fee %.
```
Handelsbanken Norden  45%   0.32%
SEB Sverige            35%   0.28%
AMF Räntefond          20%   0.12%
```

"Apply Selected Fields" button (sky-500, full width) + "Cancel" button (outline).

### Linked Cases card
- Section header: "LINKED CASES" + "New Case" button (outline, small)
- List of compact case items: title, status badge (colored pill), type badge, timestamp
- If no cases: "No cases yet" centered with `Briefcase` icon

---

## KNOWLEDGE BASE (`/knowledge`)

### Page header
"Knowledge Base" in `text-2xl font-semibold text-slate-900` (no action button).

### Search
Full-width input with `Search` icon, `placeholder="Search knowledge..."`.

### Category filter pills
Horizontal row of pills: **All** (active by default) | Product Rules | Internal Policy | Regulatory | Playbook | Precedent | FAQ | Process Guide

Active: `bg-sky-500 text-white rounded-full px-3 py-1 text-xs font-medium`. Inactive: `bg-slate-100 text-slate-600 hover:bg-slate-200 rounded-full px-3 py-1 text-xs font-medium`.

### Knowledge items (vertical list)
Each item (`rounded-xl border border-slate-200/60 bg-white shadow-sm p-5`):
- Title: `text-sm font-semibold text-slate-900` — e.g., "ITP1 — Premiebestämd tjänstepension"
- Category badge:
  - Product Rule: `bg-blue-50 text-blue-700`
  - Internal Policy: `bg-violet-50 text-violet-700`
  - Regulatory: `bg-amber-50 text-amber-700`
  - Playbook: `bg-emerald-50 text-emerald-700`
- Source: `text-xs text-slate-400` — e.g., "Collectum — ITP1-avtalet 2024"
- Tags: `bg-slate-100 text-slate-500 text-[10px] rounded px-1.5 py-0.5` — e.g., "ITP1", "premiebestämd"
- Content preview: `text-sm text-slate-600 line-clamp-3` with "Show more" / "Show less" toggle (expand to full text)
- Hover: `border-l-4 border-sky-400`

### Empty state
`BookOpen` icon `h-12 w-12 text-slate-300`, "No knowledge items found", "Try adjusting your search or category filter".

## MOCK DATA

```typescript
const clients = [
  { id: "c1", name: "Anna Johansson", dob: "1981-03-15", age: 45, employer: "Volvo Group AB", agreement: "ITP1", annualIncome: 684000, monthlyIncome: 57000, retirementAge: 65, risk: "moderate", status: "employed" },
  { id: "c2", name: "Lars Pettersson", dob: "1968-08-22", age: 58, employer: "Ericsson AB", agreement: "ITP2", annualIncome: 960000, monthlyIncome: 80000, retirementAge: 63, risk: "low", status: "employed" },
]

const knowledge = [
  { title: "ITP1 — Premiebestämd tjänstepension", category: "product_rule", source: "Collectum — ITP1-avtalet 2024", tags: ["ITP1", "premiebestämd", "collectum"], content: "ITP1 gäller för anställda födda 1979 eller senare. Premien baseras på lönen och betalas av arbetsgivaren. Den anställde väljer själv hur premierna placeras bland de valbara fonderna hos Collectum." },
  { title: "ITP2 — Förmånsbestämd tjänstepension", category: "product_rule", source: "Collectum — ITP2-avtalet 2024", tags: ["ITP2", "förmånsbestämd", "alecta"], content: "ITP2 gäller för anställda födda 1978 eller tidigare. Pensionen baseras på slutlönen och intjänandetiden. Grundtryggheten hanteras av Alecta." },
  { title: "Löneväxling — regler och förutsättningar", category: "internal_policy", source: "SPP — Intern policy 2024", tags: ["löneväxling", "salary_exchange"], content: "Löneväxling innebär att den anställde avstår en del av sin bruttolön mot en extra pensionsavsättning. Villkor: lön efter växling får inte understiga gränsen för sjukpenninggrundande inkomst." },
  { title: "IDD — Krav på behovsanalys", category: "regulatory_requirement", source: "Finansinspektionen — FFFS 2018:10", tags: ["IDD", "compliance", "FI"], content: "Enligt IDD ska en behovsanalys genomföras innan rådgivning lämnas. Analysen ska dokumenteras och innehålla kundens ekonomiska situation, mål, riskvilja och kunskapsnivå." },
  { title: "Riskprofiler — bedömning och rekommendation", category: "playbook", source: "SPP — Riskprofilsguide v3", tags: ["riskprofil", "rådgivning"], content: "Riskprofilen bestäms genom en kombination av kundens tidshorisont, ekonomiska situation och subjektiva riskvilja. Tre nivåer: låg, moderat, hög." },
  { title: "Pensionsålder och uttag — regler 2024", category: "regulatory_requirement", source: "Pensionsmyndigheten / SKV", tags: ["pensionsålder", "uttag"], content: "Tidigaste uttag av allmän pension: 63 år (höjs till 64 år 2026). Tjänstepension kan vanligtvis tas ut från 55 år. Privat pension från 55 år." },
]
```

All UI text in English, Swedish data stays Swedish. Keep the same App Shell from Part 1.
