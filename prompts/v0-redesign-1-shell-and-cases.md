# Aetherion — Part 1: App Shell, Cases Dashboard, Case Detail

Build a Next.js 14 (App Router) prototype for **Aetherion**, an AI-powered decision workspace for Swedish pension advisors. Enterprise B2B SaaS used by pension companies like SPP. The UI must communicate trust and competence — this is financial infrastructure.

Use **shadcn/ui** (New York style), **Tailwind CSS**, **Inter** font, **Lucide React** icons.

## DESIGN RULES

- **Font**: Inter only. No serif fonts.
- **Primary accent**: `sky-500` for buttons, active states. Used sparingly.
- **Sidebar**: `bg-slate-950`. Active nav: `text-sky-400 bg-sky-500/10 border-l-2 border-sky-400`. Inactive: `text-slate-400`.
- **Content area**: `bg-slate-50`. Cards: `bg-white border border-slate-200/60 shadow-sm rounded-xl`.
- **Text**: `text-slate-900` headings, `text-slate-600` body, `text-slate-400` metadata.
- **Buttons**: Primary `bg-sky-500 hover:bg-sky-600 text-white rounded-lg`. Secondary `border border-slate-200 bg-white text-slate-700 rounded-lg`.
- **Badges**: `rounded-full px-2.5 py-0.5 text-xs font-medium` with semantic colors.
- **Section headers**: `text-xs font-medium uppercase tracking-wider text-slate-400`.
- **List hover**: `border-l-4 border-transparent` → `border-l-4 border-sky-400` on hover with `transition-all duration-200`.
- **Must NOT**: use serif fonts, heavy gradients, colored card backgrounds, rounded-full cards, decorative illustrations.

## APP SHELL

### Sidebar (fixed, 256px, `bg-slate-950`)

**Logo**: Small rounded square with gradient `sky-400→blue-600` + "Aetherion" in white `text-lg font-bold`.

**Nav items** (below `border-t border-slate-800`):
- `Briefcase` "Cases" — badge "4"
- `Users` "Clients" — badge "2"
- `BookOpen` "Knowledge Base" — badge "6"

Badges: `bg-slate-800 text-slate-400 text-[10px] px-1.5 py-0.5 rounded-full`.

**User area** (bottom): "EE" initials avatar (`bg-sky-500/20 text-sky-400`), "Erik Eriksson", "Advisor" in `text-xs text-slate-500`, `Settings` gear icon.

### Top bar (sticky, `bg-white/80 backdrop-blur-sm border-b border-slate-200/60`)

Left: Breadcrumbs. Center: Fake search `bg-slate-100 rounded-lg px-3 py-1.5 text-xs text-slate-400` showing "Search... ⌘K". Right: `Bell` icon with red dot, "EE" avatar (28x28), "SPP" org badge (`bg-slate-100 rounded-full px-3 py-1 text-xs text-slate-500`).

## CASES DASHBOARD (`/cases`)

### Stats bar (grid, 4 cols)
| Icon | Number | Label | Tint |
|------|--------|-------|------|
| `Briefcase` | 4 | Active Cases | `bg-sky-50 border-sky-100` |
| `Clock` | 1 | Pending Review | `bg-amber-50 border-amber-100` |
| `Users` | 2 | Clients | `bg-emerald-50 border-emerald-100` |
| `CheckCircle` | 0 | Completed | `bg-slate-50 border-slate-100` |

### Header: "Cases" + "New Case" button (sky-500, `Plus` icon).

### Filter pills (NOT dropdowns)
Status: All | Draft | In Preparation | Ready for Review | In Review | Approved | Completed. Active: `bg-sky-500 text-white`. Inactive: `bg-slate-100 text-slate-600`. Divider `|`. Type: All | Retirement Planning | Salary Exchange | Pension Review.

### Search input below filters.

### Case cards
Each card has a **3px progress bar at top** (draft=slate 15%, in_preparation=blue 30%, ready_for_review=amber 50%, in_review=purple 70%, approved=emerald 85%, completed=green 100%). Client initials avatar on left. Title, summary (line-clamp-1), status+type badges on right. Footer: "Maria Lindqvist · Yesterday" with `Clock` icon.

### Empty state: `Inbox` icon h-12, "No cases found", hint text, "New Case" button.

## CASE DETAIL (`/cases/[id]`)

Two columns: main `flex-1` + right panel `w-[400px]`.

### Left: Case Header card
Title, summary, clickable status badge with `ChevronDown` (dropdown for status transitions), type badge.

### Left: Meeting Preparation card
Header: `ClipboardList` icon + "Meeting Preparation". Three states:
1. **Empty**: centered icon, description, "Prepare Meeting" button (sky-500, full width)
2. **Generating**: animated steps (Analyzing pension situation / Identifying key issues / Building meeting agenda)
3. **Generated**: Full brief with sections:
   - Client Overview (text)
   - Pension Situation: 3 pillar cards with colored left borders (blue=allmän, emerald=tjänste, violet=privat), total assessment below (sky border)
   - Key Issues: severity badges (red high, amber medium, slate low) with colored left borders
   - Scenarios: 2-col grid, projected outcomes, trade-offs in amber callout
   - Talking Points: numbered list
   - Open Questions: `HelpCircle` icon list
   - Agenda: timeline with topic, duration, notes, total time at top
   - "Regenerate Brief" button

### Left: Client Information card
Section header "CLIENT INFORMATION". 2-col grid: Name, Age, Employer, Collective Agreement (blue badge), Monthly Income, Risk Profile (colored badge), Retirement Age, Employment Status.

### Left: AI Recommendation card
Header: `Sparkles` icon (sky-500) + "AI Recommendation" + version badge. Three states: empty (generate button), generating (3 steps), generated (suitability score with progress bar, summary, reasoning chain timeline, assumptions, scenarios grid, evidence cards, action buttons: Generate Document / Download DOCX / Generate New Version).

### Right: Knowledge Base card
Search input. Results: expandable items with title, category badge, tags, content.

### Right: Audit Trail card
Vertical timeline: sky-500 dots for system events (`Cpu` icon), slate-300 for user events (`User` icon). Action label + timestamp.

## CREATE CASE DIALOG (triggered by "New Case" button)

shadcn/ui `Dialog` (`max-w-lg`). Title: "New Case". Form fields:
- **Client**: `Select` dropdown with client name + employer. Required.
- **Case Type**: `Select` — Retirement Planning, Salary Exchange, Pension Review, Transfer Advice, Survivor Protection. Required.
- **Title**: `Input`, auto-generated from type + client name but editable.
- **Summary**: `Textarea` (3 rows), optional.

Footer: "Cancel" (outline) + "Create Case" (sky-500). Show this dialog in the open state.

## MOCK DATA

```typescript
const cases = [
  { id: "cs1", title: "Pensionsöversikt och placeringsrådgivning — Anna Johansson", type: "Retirement Planning", status: "in_preparation", summary: "Anna, 45 år, ITP1 via Volvo. Vill se över sin tjänstepension.", advisor: "Maria Lindqvist", updated: "Yesterday" },
  { id: "cs2", title: "Löneväxlingsanalys — Lars Pettersson", type: "Salary Exchange", status: "in_preparation", summary: "Lars, 58 år, ITP2 via Ericsson. Hög lön, vill utreda löneväxling.", advisor: "Maria Lindqvist", updated: "2 days ago" },
  { id: "cs3", title: "Fondval och avgiftsöversyn — Anna Johansson", type: "Pension Review", status: "ready_for_review", summary: "Uppföljning av Annas fondval hos Collectum.", advisor: "Erik Eriksson", updated: "Today" },
  { id: "cs4", title: "Familjeskydd — Lars Pettersson", type: "Survivor Protection", status: "draft", summary: "Översyn av Lars familjeskydd.", advisor: "Erik Eriksson", updated: "3 days ago" },
]
```

Build the App Shell as a dashboard layout, Cases Dashboard, and Case Detail (show the "generated" meeting brief state and recommendation state with realistic mock content). All UI text in English, Swedish data stays Swedish.
