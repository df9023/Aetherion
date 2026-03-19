# v0 Prompt 1/3 — App Shell + Cases Dashboard

> **CRITICAL DESIGN INSTRUCTION**: This must look like a premium, modern tech product — think Linear, Vercel Dashboard, or Legora (legora.com). It must NOT look like a basic HTML page. Use the shadcn/ui "New York" style variant. Use `font-sans` (Geist Sans or Inter via `next/font`). NEVER use serif fonts like Times New Roman. Every surface must have intentional styling.

## What to build

Build the **app shell** (sidebar + top bar layout) and the **Cases Dashboard** for Aetherion — an AI-native decision platform for pension and retirement institutions. This is a Next.js 14 app (App Router) using **shadcn/ui (New York style)**, **Tailwind CSS**, and **React Query** (`@tanstack/react-query`).

The target user is a pension advisor at a regulated financial institution. They use this daily to manage cases, generate AI recommendations, and produce compliant documentation.

---

## Design System — Legora-inspired Modern SaaS

This must look and feel like **Legora** (legora.com) — a premium Swedish AI platform. Clean, dark sidebar, sophisticated, tech-forward. NOT a generic template. NOT a basic HTML page.

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

Configure these in `globals.css` using shadcn/ui CSS variables:

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
- **Accent/CTA buttons**: `bg-sky-500 hover:bg-sky-600 text-white` — `rounded-lg`, not fully rounded
- **Secondary buttons**: `bg-slate-100 hover:bg-slate-200 text-slate-700`
- **Status badges** — use shadcn Badge with custom color variants:
  - Draft: `bg-slate-100 text-slate-600`
  - In Preparation: `bg-blue-50 text-blue-700 border border-blue-200`
  - Ready for Review: `bg-amber-50 text-amber-700 border border-amber-200`
  - In Review: `bg-purple-50 text-purple-700 border border-purple-200`
  - Approved: `bg-emerald-50 text-emerald-700 border border-emerald-200`
  - Completed: `bg-green-50 text-green-800 border border-green-200`
  - Archived: `bg-slate-50 text-slate-400`

### Component Styling Rules

- **Cards**: Always `rounded-xl`, never `rounded` or `rounded-md`. Subtle `shadow-sm`. Border `border-slate-200/60`.
- **Buttons**: `rounded-lg` (not fully round). Primary = `bg-sky-500`. Height `h-10` for normal, `h-12` for hero CTAs.
- **Inputs**: `rounded-lg bg-slate-50 border-slate-200 focus:ring-sky-500`
- **Badges**: Small, `rounded-full`, `text-xs font-medium`, `px-2.5 py-0.5`
- **Hover on cards**: `hover:shadow-md hover:border-slate-300 transition-all duration-200`
- **Icons**: Lucide React, size `w-4 h-4`, color `text-slate-400` unless active
- **Separators**: `border-slate-100`, very subtle

### What It Must NOT Look Like

- **NO serif fonts** — no Times New Roman, no Georgia, no default browser font
- **NO unstyled HTML** — every element must have explicit Tailwind classes
- **NO bright gradients or neon colors**
- **NO generic Bootstrap/Material look**
- **NO heavy borders or boxy layouts**
- **NO default browser link styling** (blue underlined links)
- If it looks like a 2005 website or a plain HTML form, you've failed

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

---

## Component 1: App Shell / Layout

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
- Right: Org badge ("NordPension Rådgivning AB") as `text-xs font-medium text-slate-500 bg-slate-100 px-3 py-1 rounded-full`

**Main content area** — `ml-64 min-h-screen bg-slate-50`

---

## Component 2: Cases Dashboard (`/cases`)

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

**Cases list** — `space-y-3`. Each case is a clickable card, NOT a raw table:

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
- Type badge: `bg-slate-100 text-slate-600 text-xs rounded-full px-2.5 py-0.5`
- Status badge: colored per status (see color system above)
- Date: `text-xs text-slate-400` right-aligned
- Assigned to: `text-sm text-slate-500` with small `User` icon
- Click → navigates to `/cases/[id]`

### Mock Data for the Dashboard

Use this hardcoded data to populate the dashboard (2 cases):

```typescript
const mockCases = [
  {
    id: "case-1",
    title: "Anna Johansson — Retirement Planning",
    case_type: "retirement_planning",
    status: "in_preparation",
    summary: "ITP1 pension review and withdrawal strategy for client approaching retirement",
    client_id: "client-1",
    assigned_to: "user-1",
    assignee_name: "Erik Eriksson",
    created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: "case-2",
    title: "Lars Pettersson — Salary Exchange",
    case_type: "salary_exchange",
    status: "draft",
    summary: "Löneväxling analysis for ITP2 client at Ericsson",
    client_id: "client-2",
    assigned_to: "user-2",
    assignee_name: "Maria Lindqvist",
    created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date().toISOString(),
  },
]
```

---

## Technical Details

- Use Next.js App Router (`app/` directory)
- Use **shadcn/ui (New York style)** components: `Card`, `Badge`, `Button`, `Input`, `Select`, `Avatar`, `Breadcrumb`, `Separator`, `Skeleton`
- All UI text is in **English**. Swedish terms in data (org names, pension types like ITP1) stay as-is.
- Use `@tanstack/react-query` for data fetching (can use mock data for now)

### Routing structure

```
app/
  layout.tsx          → App shell (sidebar + top bar)
  cases/
    page.tsx          → Cases dashboard (this prompt)
  clients/
    page.tsx          → (placeholder for prompt 2)
  knowledge/
    page.tsx          → (placeholder for prompt 3)
```

---

## Design Checklist

Before outputting, verify:
- [ ] Font is Inter — NO serif fonts anywhere
- [ ] Sidebar is dark (`bg-slate-950`) with light text and sky-400 active state
- [ ] Page background is `bg-slate-50`, not pure white
- [ ] All cards use `rounded-xl border border-slate-200/60 shadow-sm`
- [ ] Primary buttons are `bg-sky-500` with `rounded-lg`
- [ ] Badges are `rounded-full text-xs font-medium` with status-appropriate colors
- [ ] All text uses `text-slate-*` color scale
- [ ] Icons are Lucide React, `w-4 h-4`, `text-slate-400` unless active
- [ ] The overall feel matches Legora.com / Linear.app / Vercel Dashboard
- [ ] It does NOT look like a basic HTML page or a 2005 website
