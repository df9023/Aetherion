# Aetherion — Complete Frontend Prototype

Build a Next.js 14 (App Router) prototype for **Aetherion**, an AI-powered decision workspace for Swedish pension advisors. This is an enterprise B2B SaaS product used by pension companies like SPP. The UI must communicate trust, competence, and clarity — this is financial infrastructure, not a consumer app.

Use **shadcn/ui** (New York style), **Tailwind CSS**, **Inter** font, and **Lucide React** icons.

---

## CRITICAL DESIGN RULES

### Visual identity
- **Font**: Inter. No serif fonts anywhere. No monospace except code.
- **Primary accent**: `sky-500` (#0ea5e9) for buttons, active states, links. Use sparingly — most of the UI is neutral.
- **Sidebar**: `bg-slate-950` (near-black). Nav text in `text-slate-400`, active in `text-sky-400` with `bg-sky-500/10` and a `border-l-2 border-sky-400`.
- **Content area**: `bg-slate-50` background. Cards are `bg-white` with `border border-slate-200/60` and `shadow-sm`.
- **Text hierarchy**: `text-slate-900` for headings, `text-slate-600` for body, `text-slate-400` for metadata/labels.

### Component patterns
- **Cards**: `rounded-xl border border-slate-200/60 bg-white shadow-sm`. No gradients on cards. No colored backgrounds on cards (except subtle status tints).
- **Buttons**: Primary: `bg-sky-500 hover:bg-sky-600 text-white rounded-lg`. Secondary: `border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 rounded-lg`.
- **Badges/pills**: `rounded-full px-2.5 py-0.5 text-xs font-medium` with semantic colors (emerald for success, amber for warning, red for error, blue for info, slate for neutral).
- **Section headers**: `text-xs font-medium uppercase tracking-wider text-slate-400` (muted, structural labels).
- **Inputs**: `rounded-lg border-slate-200` with subtle focus ring.
- **Hover on list items**: `border-l-4 border-transparent hover:border-l-4 hover:border-sky-400 transition-all duration-200`.

### What it must NOT look like
- No Times New Roman, Georgia, or serif fonts anywhere
- No heavy gradients or glassmorphism
- No bright colored card backgrounds
- No overly rounded elements (max `rounded-xl` for cards, `rounded-lg` for buttons)
- No decorative illustrations or mascots
- No vibecoded aesthetic — this is financial software, not a social app

---

## PAGE 1: APP SHELL (Dashboard Layout)

### Sidebar (fixed, left, 256px wide, `bg-slate-950`)

**Logo area** (top):
- A small rounded square (20x20px) with a gradient from `sky-400` to `blue-600` — the Aetherion logo mark.
- "Aetherion" in white, `text-lg font-bold`, next to the logo.

**Navigation** (below logo, after a `border-t border-slate-800` separator):
Three nav items, each with an icon and a count badge:
- `Briefcase` icon — "Cases" — badge showing "4"
- `Users` icon — "Clients" — badge showing "2"
- `BookOpen` icon — "Knowledge Base" — badge showing "6"

Active state: `border-l-2 border-sky-400 bg-sky-500/10 text-sky-400`. Inactive: `text-slate-400 hover:bg-slate-800/50 hover:text-slate-100`.

Count badges: `bg-slate-800 text-slate-400 text-[10px] font-medium px-1.5 py-0.5 rounded-full` aligned to the right of each item.

**User area** (bottom, above `border-t border-slate-800`):
- Initials avatar: `bg-sky-500/20 text-sky-400 text-xs font-medium` in a 32x32 rounded-full circle showing "EE"
- Name: "Erik Eriksson" in `text-sm font-medium text-slate-200`
- Role: "Advisor" in `text-xs text-slate-500`
- Settings gear icon (`Settings` from Lucide) in `text-slate-500 hover:text-slate-300`

### Top bar (sticky, full width minus sidebar, `bg-white/80 backdrop-blur-sm border-b border-slate-200/60`)

Left side:
- Breadcrumbs using shadcn/ui `Breadcrumb` component. Example: "Cases" or "Cases > Anna Johansson — Retirement Planning"

Center-ish:
- A fake search element: `bg-slate-100 rounded-lg px-3 py-1.5` containing `text-xs text-slate-400` reading "Search..." with a `⌘K` badge (`bg-slate-200 rounded px-1 py-0.5 text-[10px] text-slate-500`).

Right side:
- Notification bell (`Bell` icon) with a small red dot indicator (4px, absolute positioned top-right). `text-slate-400 hover:text-slate-600`.
- Initials avatar "EE" (same style as sidebar but smaller, 28x28).
- Org badge: `bg-slate-100 rounded-full px-3 py-1 text-xs font-medium text-slate-500` reading "SPP".

---

## PAGE 2: CASES DASHBOARD (`/cases`)

### Stats bar
A row of 4 compact metric cards at the top, in a `grid grid-cols-4 gap-4`:

| Icon | Number | Label | Card tint |
|------|--------|-------|-----------|
| `Briefcase` | 4 | Active Cases | `bg-sky-50 border-sky-100` |
| `Clock` | 1 | Pending Review | `bg-amber-50 border-amber-100` |
| `Users` | 2 | Clients | `bg-emerald-50 border-emerald-100` |
| `CheckCircle` | 0 | Completed | `bg-slate-50 border-slate-100` |

Each card: `rounded-xl p-4 border`. Icon in matching color (sky-500, amber-500, etc.), `text-2xl font-bold text-slate-900` for the number, `text-xs text-slate-500` for the label.

### Page header
- `text-2xl font-semibold text-slate-900` "Cases"
- "New Case" button: `bg-sky-500 hover:bg-sky-600 text-white rounded-lg` with `Plus` icon.

### Filters
A horizontal row of pills (NOT select dropdowns):

**Status pills**: All (active) | Draft | In Preparation | Ready for Review | In Review | Approved | Completed
**Type pills**: All (active) | Retirement Planning | Salary Exchange | Pension Review | Transfer Advice

Active pill: `bg-sky-500 text-white`. Inactive: `bg-slate-100 text-slate-600 hover:bg-slate-200`. All pills `rounded-full px-3 py-1 text-xs font-medium`.

Subtle vertical divider `|` in `text-slate-300` between the two groups.

### Search
Below filters: search input with `Search` icon, `placeholder="Search cases..."`.

### Case list
Vertical stack of case cards. Each card:

```
┌─[progress bar: thin 3px colored bar at top, width based on status]──────┐
│                                                                          │
│  [AJ]  Pensionsöversikt — Anna Johansson          [In Preparation] [RP] │
│        Anna, 45 år, ITP1 via Volvo...                                    │
│                                                                          │
│        Maria Lindqvist · Yesterday                                       │
└──────────────────────────────────────────────────────────────────────────┘
```

- Progress bar colors: draft=slate-300 15%, in_preparation=blue-400 30%, ready_for_review=amber-400 50%, in_review=purple-400 70%, approved=emerald-400 85%, completed=green-500 100%.
- `[AJ]` is client initials in a `h-9 w-9 rounded-full bg-slate-100 text-sm font-medium text-slate-600` circle.
- Title: `text-sm font-semibold text-slate-900`.
- Summary: `text-sm text-slate-500 line-clamp-1`.
- Status badge: colored pill per status. Type badge: `bg-slate-100 text-slate-600`.
- Footer: advisor name + timestamp in `text-xs text-slate-400` with `Clock` icon.
- Hover: `border-l-4 border-sky-400` slides in from left.

### Empty state (when no results)
- `Inbox` icon `h-12 w-12 text-slate-300` centered
- "No cases found" in `text-sm font-medium text-slate-600`
- "Try adjusting your filters or create a new case" in `text-xs text-slate-400`
- "New Case" button below

### Create Case dialog (triggered by "New Case" button)
shadcn/ui `Dialog` with `DialogContent` (`max-w-lg`). Title: "New Case".

Form fields (vertical stack, `space-y-4`):
- **Client**: `Select` dropdown populated from the clients list. Shows client name + employer. Required.
- **Case Type**: `Select` with options: Retirement Planning, Salary Exchange, Pension Review, Transfer Advice, Survivor Protection. Required.
- **Title**: `Input`, auto-generated from type + client name but editable. e.g., "Pensionsöversikt — Anna Johansson".
- **Summary**: `Textarea` (3 rows), placeholder "Brief description of the case...". Optional.

Footer: "Cancel" button (outline) + "Create Case" button (sky-500). On success, redirects to the new case detail page.

---

## PAGE 3: CASE DETAIL (`/cases/[id]`)

Two-column layout: main content `flex-1` on left, sidebar panel `w-[400px]` on right.

### Left column

**Case header card**:
- Title: `text-xl font-semibold text-slate-900` — "Pensionsöversikt och placeringsrådgivning — Anna Johansson"
- Summary: `text-sm text-slate-500`
- Status badge (clickable, with `ChevronDown` icon to show dropdown of valid next statuses)
- Type badge
- Meeting date if set

**Meeting Preparation card** (NEW — this is a key feature):
- Header: `ClipboardList` icon + "Meeting Preparation" in `text-lg font-semibold`
- Empty state: centered icon, description text, and full-width "Prepare Meeting" button (`bg-sky-500`)
- Generating state: animated step indicators (Analyzing pension situation... / Identifying key issues... / Building meeting agenda...)
- Generated state: the full meeting brief rendered in sections:
  - **Client Overview**: text block
  - **Pension Situation**: 3 pillar cards in a row, each with colored left border (blue=allmän pension, emerald=tjänstepension, violet=privat pension), plus a full-width total assessment below with sky left border
  - **Key Issues**: list of issues with severity badges (red/amber/slate) and colored left borders
  - **Scenarios**: 2-column grid of scenario cards with projected outcomes (key-value pairs) and trade-offs in amber callout
  - **Talking Points**: numbered list
  - **Open Questions**: list with `HelpCircle` icons
  - **Agenda**: timeline showing topic, duration (e.g., "15 min"), and notes. Total time shown at top.
  - "Regenerate Brief" button at bottom

**Client Information card**:
- Section header: "CLIENT INFORMATION"
- Two-column grid: Name, Age, Employer (with `Building2` icon), Collective Agreement (blue badge), Monthly Income, Risk Profile (colored badge), Desired Retirement Age (with `Target` icon), Employment Status

**AI Recommendation card**:
- Header: `Sparkles` icon (sky-500) + "AI Recommendation" + version badge
- Empty state: centered sparkles icon, description, optional context textarea, full-width "Generate Recommendation" button
- Generating state: 3 animated steps
- Generated state:
  - Suitability score: large number (e.g., "8.5") with color coding (green ≥8, amber ≥6, red <6) and a progress bar
  - Summary text
  - Reasoning chain: vertical timeline with numbered sky-500 circles, step description, conclusion, evidence pills
  - Assumptions: cards with amber "impact if wrong" callouts
  - Scenarios: 2-column grid with projected outcome key-value pairs
  - Evidence: cards with source type badge, reference, snippet, confidence bar
  - Action buttons: "Generate Document" (sky-500), "Download DOCX" (outline), "Generate New Version" (outline)

### Right column

**Knowledge Base card**:
- Header: "KNOWLEDGE BASE"
- Search input with `Search` icon
- Results as expandable items: title, category badge, tags, expandable content

**Audit Trail card**:
- Header: "AUDIT TRAIL"
- Vertical timeline: colored dots (sky-500 for system, slate-300 for user), action label, timestamp
- System actions show `Cpu` icon, user actions show `User` icon

---

## PAGE 4: CLIENTS LIST (`/clients`)

### Page header
- "Clients" heading + "New Client" button (sky-500)

### Search
- Search input with `Search` icon

### Client cards (grid, 3 columns on large screens)
Each card:
- Initials avatar (larger, `h-10 w-10`)
- Name: `text-sm font-semibold text-slate-900`
- Age: `text-xs text-slate-400`
- Employer with `Building2` icon
- Monthly income
- Risk profile badge (green=low, amber=moderate, red=high) with `Shield` icon
- Hover: `border-l-4 border-sky-400`

Cards link to `/clients/[id]`.

### Empty state
- `Users` icon, "No clients found", "Create your first client to get started", "New Client" button

### Create Client dialog (triggered by "New Client" button)
shadcn/ui `Dialog` with `DialogContent` (`max-w-2xl`). Title: "New Client".

Form fields in a two-column grid (`grid grid-cols-2 gap-4`):
- **First Name**: `Input`, required.
- **Last Name**: `Input`, required.
- **Date of Birth**: `Input` (type date), required.
- **Employer**: `Input`, placeholder "e.g., Volvo Group AB".
- **Collective Agreement**: `Select` with options: ITP1, ITP2, SAF-LO, KAP-KL, PA 16, Other. Optional.
- **Annual Income**: `Input` (type number), placeholder "e.g., 684000". In SEK.
- **Employment Status**: `Select` with options: Employed, Self-employed, Retired, Unemployed. Default: Employed.
- **Risk Profile**: `Select` with options: Low, Moderate, High. Optional.
- **Desired Retirement Age**: `Input` (type number), placeholder "e.g., 65". Optional.

Footer: "Cancel" button (outline) + "Create Client" button (sky-500).

---

## PAGE 5: CLIENT DETAIL (`/clients/[id]`)

### Client header card
- Large initials avatar (`h-14 w-14`)
- Name: `text-xl font-semibold text-slate-900`
- Date of birth + age, employment status badge

### Details card
- Section header: "DETAILS"
- Two-column grid: Employer, Collective Agreement (blue badge), Annual Income, Monthly Income, Desired Retirement Age, Risk Profile (colored badge), Employment Status

### Document Ingestion card (NEW — key feature)
- Header: `Upload` icon + "Document Ingestion"
- **Upload state**: Dashed border dropzone (`border-2 border-dashed border-slate-300 rounded-xl`). `Upload` icon centered, "Upload pension document" text, "Drop a PDF here or click to browse" subtext. Accepts .pdf files.
- **Extracting state**: Progress indicators — "Extracting text from document..." / "Analyzing pension data..." / "Building structured output..."
- **Review state**: Two-column grid of extracted fields. Each field shows:
  - Field name (e.g., "Collective Agreement")
  - Extracted value in `font-medium`
  - Confidence indicator: green checkmark (>80%), amber warning (50-80%), red flag (<50%)
  - Checkbox to include/exclude from update
  - If different from current value: show `current value → extracted value` with the arrow in slate-400
  - Fund allocations shown in a small table (fund name, allocation %, fee %)
  - "Apply Selected Fields" button (sky-500) + "Cancel" button (outline)

### Linked Cases card
- Header: "LINKED CASES" + "New Case" button (outline, small)
- List of case cards (compact version: title, status badge, type badge, timestamp)
- Empty state: "No cases yet"

---

## PAGE 6: KNOWLEDGE BASE (`/knowledge`)

### Page header
- "Knowledge Base" heading (no button — knowledge is added via document ingestion or backend)

### Search
- Full-width search input with `Search` icon

### Category filter pills
Horizontal row: All | Product Rules | Internal Policy | Regulatory | Playbook | Precedent | FAQ | Process Guide

Active: `bg-sky-500 text-white`. Inactive: `bg-slate-100 text-slate-600`.

### Knowledge items (vertical list)
Each item:
- Title: `text-sm font-semibold text-slate-900`
- Category badge (colored per category: blue=product rule, violet=internal policy, amber=regulatory, emerald=playbook)
- Source: `text-xs text-slate-400`
- Tags: small pills `bg-slate-100 text-slate-500 text-[10px] rounded px-1.5 py-0.5`
- Content: `line-clamp-3 text-sm text-slate-600` with "Show more" / "Show less" toggle
- Hover: `border-l-4 border-sky-400`

### Empty state
- `BookOpen` icon, "No knowledge items found", subtext

---

## MOCK DATA

Use this data to populate the prototype:

```typescript
const currentUser = { name: "Erik Eriksson", role: "Advisor", initials: "EE" }
const org = { name: "SPP" }

const clients = [
  { id: "c1", name: "Anna Johansson", dob: "1981-03-15", age: 45, employer: "Volvo Group AB", agreement: "ITP1", income: 684000, retirementAge: 65, risk: "moderate", status: "employed" },
  { id: "c2", name: "Lars Pettersson", dob: "1968-08-22", age: 58, employer: "Ericsson AB", agreement: "ITP2", income: 960000, retirementAge: 63, risk: "low", status: "employed" },
]

const cases = [
  { id: "cs1", title: "Pensionsöversikt och placeringsrådgivning — Anna Johansson", type: "retirement_planning", status: "in_preparation", summary: "Anna, 45 år, ITP1 via Volvo. Vill se över sin tjänstepension och eventuellt göra ett aktivt fondval.", clientId: "c1", advisor: "Maria Lindqvist", updated: "Yesterday" },
  { id: "cs2", title: "Löneväxlingsanalys — Lars Pettersson", type: "salary_exchange", status: "in_preparation", summary: "Lars, 58 år, ITP2 via Ericsson. Hög lön (80 000 kr/mån). Vill utreda löneväxling.", clientId: "c2", advisor: "Maria Lindqvist", updated: "2 days ago" },
  { id: "cs3", title: "Fondval och avgiftsöversyn — Anna Johansson", type: "pension_review", status: "ready_for_review", summary: "Uppföljning av Annas fondval hos Collectum. Jämförelse av avgifter.", clientId: "c1", advisor: "Erik Eriksson", updated: "Today" },
  { id: "cs4", title: "Familjeskydd — Lars Pettersson", type: "survivor_protection", status: "draft", summary: "Översyn av Lars familjeskydd och efterlevandepension.", clientId: "c2", advisor: "Erik Eriksson", updated: "3 days ago" },
]

const knowledge = [
  { title: "ITP1 — Premiebestämd tjänstepension", category: "product_rule", source: "Collectum — ITP1-avtalet 2024", tags: ["ITP1", "premiebestämd", "collectum"] },
  { title: "ITP2 — Förmånsbestämd tjänstepension", category: "product_rule", source: "Collectum — ITP2-avtalet 2024", tags: ["ITP2", "förmånsbestämd", "alecta"] },
  { title: "Löneväxling — regler och förutsättningar", category: "internal_policy", source: "SPP — Intern policy 2024", tags: ["löneväxling", "salary_exchange"] },
  { title: "IDD — Krav på behovsanalys", category: "regulatory_requirement", source: "Finansinspektionen — FFFS 2018:10", tags: ["IDD", "compliance", "FI"] },
  { title: "Riskprofiler — bedömning och rekommendation", category: "playbook", source: "SPP — Riskprofilsguide v3", tags: ["riskprofil", "rådgivning"] },
  { title: "Pensionsålder och uttag — regler 2024", category: "regulatory_requirement", source: "Pensionsmyndigheten / SKV", tags: ["pensionsålder", "uttag"] },
]
```

---

## IMPORTANT

- Build ALL 6 pages as separate routes
- Use the App Router (`app/` directory)
- The sidebar and top bar are shared via a dashboard layout
- All content is in English (UI labels), but Swedish data (case titles, knowledge content) stays in Swedish
- Make it look like a product that a pension company CTO would pay for — not a prototype
