# Aetherion — Part 3: Create Case & Create Client Dialogs

This is Part 3 of the Aetherion frontend prototype. **Parts 1-2 already built the App Shell, Cases pages, Clients pages, and Knowledge Base.** This prompt adds the two "create" dialogs. Keep the exact same design system.

Use **shadcn/ui** (New York style), **Tailwind CSS**, **Inter** font, **Lucide React** icons.

## DESIGN RULES (same as Parts 1-2)

- Cards: `bg-white border border-slate-200/60 shadow-sm rounded-xl`
- Buttons: Primary `bg-sky-500 hover:bg-sky-600 text-white rounded-lg`. Secondary `border border-slate-200 bg-white text-slate-700 rounded-lg`.
- Inputs: `rounded-lg border-slate-200` with subtle focus ring.
- Labels: `text-sm font-medium text-slate-700` above each input.
- No serif fonts, no gradients, no decorative elements.

---

## CREATE CASE DIALOG

Triggered by the "New Case" button on the Cases Dashboard. Use shadcn/ui `Dialog` with `DialogContent` (`max-w-lg`).

**Header**: `DialogTitle` — "New Case"

**Form** (vertical stack, `space-y-4`):

1. **Client** — shadcn/ui `Select`. Label: "Client". Placeholder: "Select a client...". Options show client name + employer in muted text:
   - "Anna Johansson" — `text-xs text-slate-400` "Volvo Group AB"
   - "Lars Pettersson" — `text-xs text-slate-400` "Ericsson AB"
   - Required. Show red `text-xs text-destructive` "Required" if submitted empty.

2. **Case Type** — shadcn/ui `Select`. Label: "Case Type". Options:
   - Retirement Planning
   - Salary Exchange
   - Pension Review
   - Transfer Advice
   - Survivor Protection
   - Required.

3. **Title** — `Input`. Label: "Title". Pre-filled based on type + client selection, e.g., "Pensionsöversikt — Anna Johansson". Editable.

4. **Summary** — `Textarea` (3 rows). Label: "Summary". Placeholder: "Brief description of the case...". Optional.

**Footer** (`DialogFooter`, `flex justify-end gap-2`):
- "Cancel" button (secondary/outline)
- "Create Case" button (sky-500 primary)

**Show the dialog in the open state** with "Anna Johansson" selected as client and "Retirement Planning" as type, so the title field is pre-filled with "Pensionsöversikt — Anna Johansson".

---

## CREATE CLIENT DIALOG

Triggered by the "New Client" button on the Clients page. Use shadcn/ui `Dialog` with `DialogContent` (`max-w-2xl`).

**Header**: `DialogTitle` — "New Client"

**Form** (two-column grid, `grid grid-cols-2 gap-x-4 gap-y-4`):

Row 1:
- **First Name** — `Input`. Placeholder: "Anna". Required.
- **Last Name** — `Input`. Placeholder: "Johansson". Required.

Row 2:
- **Date of Birth** — `Input` (type date). Required.
- **Employer** — `Input`. Placeholder: "e.g., Volvo Group AB". Optional.

Row 3:
- **Collective Agreement** — shadcn/ui `Select`. Placeholder: "Select agreement...". Options: ITP1, ITP2, SAF-LO, KAP-KL, PA 16, Other. Optional.
- **Annual Income** — `Input` (type number). Placeholder: "e.g., 684000". Label includes `text-xs text-slate-400` "SEK" hint. Optional.

Row 4:
- **Employment Status** — shadcn/ui `Select`. Options: Employed, Self-employed, Retired, Unemployed. Default: "Employed".
- **Risk Profile** — shadcn/ui `Select`. Placeholder: "Select risk profile...". Options: Low, Moderate, High. Optional.

Row 5 (single column, `col-span-2` or just left column):
- **Desired Retirement Age** — `Input` (type number). Placeholder: "e.g., 65". Optional.

**Footer** (`DialogFooter`, `flex justify-end gap-2`):
- "Cancel" button (secondary/outline)
- "Create Client" button (sky-500 primary)

**Show the dialog in the open state** with some fields pre-filled: First Name "Anna", Last Name "Johansson", Employer "Volvo Group AB", Employment Status "Employed" — so v0 renders a realistic-looking filled form.
