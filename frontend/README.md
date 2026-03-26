# Aetherion Frontend

Next.js 14 (App Router) with shadcn/ui (New York), Tailwind CSS, and React Query.

## Quick Start

```bash
npm install
npm run dev          # http://localhost:3000
```

Requires the backend running at `http://localhost:8000`. See root `SETUP.md`.

## Architecture

- `app/(dashboard)/` — All pages behind the app shell (sidebar + top bar)
- `components/` — Feature components (meeting brief viewer, document ingestion, dialogs)
- `components/ui/` — shadcn/ui primitives
- `lib/api.ts` — API client with dev auth headers
- `lib/hooks.ts` — React Query hooks for all backend endpoints
- `lib/labels.ts` — Status/category labels and color maps

## Data Layer

All data comes from the backend via React Query. No mock data in production code.

- `useQuery` hooks for reads (cases, clients, knowledge, recommendations, audit)
- `useMutation` hooks for writes (create case/client, generate recommendation/brief, upload document)
- Dev auth bypass via `X-Dev-User-Id` / `X-Dev-Org-Id` headers (configured in `.env.local`)
