# CLAUDE.md — Aetherion (Drident) Project Context for Claude Code

## What is Aetherion?

Aetherion (product name: Drident) is an AI-native decision workspace for pension, retirement, and long-term savings institutions. Advisors manage cases, generate compliance-ready recommendations with verified citations, and produce IDD-compliant documentation — with AI handling the heavy lifting and deterministic code handling the math.

Starting market: Swedish occupational pension advisory workflows. Example org in dev: **SPP**.

## Architecture

Monolithic FastAPI backend + Next.js 14 frontend. PostgreSQL + pgvector for data and embeddings.

See `docs/ARCHITECTURE_DECISIONS.md` for rationale on all major decisions.

## Core Modules

1. **Workbench** — advisor-facing case workspace (`frontend/`)
2. **Reasoner** — two-pass LLM: tool_use (structured fields) + Citations API (verified evidence). Reasoning Trail with advisor annotations and compliance sign-off. (`backend/app/services/reasoner.py`)
3. **Control** — compliance checks, audit trail, IDD-compliant document generation from reasoning chain (`backend/app/services/control.py`, `backend/app/services/document.py`)
4. **Memory** — RAG over institutional knowledge + Firm Memory (advisor insights). pgvector for embeddings, document ingestion pipeline. (`backend/app/services/memory.py`)
5. **Flow** — workflow orchestration (`backend/app/services/flow.py`)
6. **Deterministic Engine** — suitability scoring, pension calculations, eligibility checks — all computed in code, not by LLM (`backend/app/services/suitability.py`, `pension_calculator.py`, `eligibility.py`)

## Drident Capabilities

Three differentiating features (see `drident-next-capabilities.md` for full spec):

1. **Reasoning Trail** (built) — AI reasoning chain is the compliance record. Advisors annotate steps, compliance reviewers sign off. Documents generated from the chain.
2. **Firm Memory** (Phase 1 built) — advisor insights scoped by case type, collective agreement, client org. Surfaced contextually in future cases. Phase 2 (pattern detection) and Phase 3 (recommendation integration) planned.
3. **Regulatory Pulse** (planned) — monitors regulatory changes and traces impact through active cases.

## Key Reference Documents

- `docs/DOMAIN_MODEL.md` — all data entities, relationships, and design principles
- `docs/RAG_PIPELINE.md` — Memory module ingestion, chunking, embedding, retrieval
- `docs/COMPLIANCE_SPEC.md` — recommendation pack structure, audit trail requirements
- `docs/ARCHITECTURE_DECISIONS.md` — ADRs explaining why things are built the way they are
- `drident.md` — product description, capabilities, privacy/security positioning
- `drident-next-capabilities.md` — full spec for Regulatory Pulse, Reasoning Trail, Firm Memory

## Coding Standards

- Python: type hints everywhere, Pydantic for all schemas, async endpoints, service layer pattern
- TypeScript: strict mode, no `any`, functional components, React Query for server state
- All LLM prompts in `backend/app/prompts/` as Jinja2 templates, never hardcoded
- All LLM outputs parsed into Pydantic models, never stored as raw text
- Every case/recommendation state change creates an AuditEntry
- Multi-tenant: always scope queries by organization_id
- Never log PII in plaintext
- All frontend text in Swedish

## Tech Stack

- Backend: Python 3.11+ / FastAPI
- Frontend: Next.js 14 / React / TypeScript / shadcn/ui (New York) / Tailwind CSS
- Database: PostgreSQL 16 + pgvector
- LLM: Anthropic Claude API — two-pass architecture: tool_use (structured output) + Citations API (verified evidence)
- Embeddings: Voyage AI voyage-3 (primary) or OpenAI text-embedding-3-small (fallback); hash-based fake embeddings in dev without API keys. Planned: local HuggingFace model.
- Auth: WorkOS (backend integrated: login, callback, logout, /me), dev bypass via X-Dev-User-Id / X-Dev-Org-Id headers
- Doc generation: python-docx, WeasyPrint, Jinja2
- PDF extraction: pdfplumber
- Testing: pytest + pytest-asyncio + httpx AsyncClient (187+ tests)
- Infra: Docker Compose (dev), Azure EU-region or Railway (prod, planned)

## Common Commands

```bash
# Infrastructure
docker compose up db -d              # Start PostgreSQL (pgvector)

# Backend
cd backend
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Database
alembic upgrade head                 # Run migrations
python -m scripts.seed               # Seed dev data (SPP org, users, clients, client orgs, cases, knowledge docs)

# Frontend
cd frontend
npm install
npm run dev                          # http://localhost:3000

# Tests
cd backend && pytest                 # 187+ tests, ~3 seconds
```

## Key Backend Endpoints

- `POST /api/v1/cases/{id}/generate-recommendation` — AI recommendation with reasoning chain
- `POST /api/v1/cases/{id}/generate-brief` — Meeting brief generation
- `PATCH /api/v1/recommendations/{id}/reasoning/{step}/annotate` — Advisor annotation on reasoning step
- `POST /api/v1/recommendations/{id}/reasoning/review` — Compliance sign-off on reasoning chain
- `POST /api/v1/recommendations/{id}/generate-document` — Compliance doc (DOCX/PDF)
- `GET /api/v1/documents/{id}/download` — Download generated document
- `POST /api/v1/clients/{id}/ingest-document` — PDF upload + AI data extraction
- `POST /api/v1/clients/{id}/apply-extraction` — Apply extracted data to client profile
- `POST /api/v1/knowledge/search` — Semantic search over knowledge base
- CRUD: `/api/v1/cases`, `/api/v1/clients`, `/api/v1/client-organizations`, `/api/v1/firm-insights`, `/api/v1/knowledge`
- `GET /api/v1/firm-insights/relevant?case_id=uuid` — Contextual firm insight matching
- `GET /api/v1/audit/recent` — Org-wide recent audit entries (dashboard)

## Frontend Pages

- `/dashboard` — advisor home screen (metrics, activity, meetings, quick actions)
- `/cases` — case list with search, filters
- `/cases/[id]` — case detail (client info, reasoning trail, recommendation, meeting brief, firm insights, knowledge, audit)
- `/clients` — client list
- `/clients/[id]` — client detail with document ingestion
- `/organizations` — client organizations (employer companies)
- `/organizations/[id]` — org detail with employee list
- `/knowledge` — knowledge base with search, categories, upload
- `/insights` — firm insights browsing, filtering, creation

## Frontend Data Layer

- API client: `frontend/lib/api.ts` (apiFetch, apiUpload, apiDownload with dev auth headers)
- React Query hooks: `frontend/lib/hooks.ts` (all backend endpoints wired)
- UI labels/styles: `frontend/lib/labels.ts` (all Swedish)
- Providers: `frontend/components/providers.tsx` (QueryClientProvider)

## Two-Pass Recommendation Architecture

1. **Pass 1 (tool_use):** Returns structured fields — summary, assumptions, scenarios, suitability_score, cost_disclosure, conflict_disclosure. Prompt: `backend/app/prompts/recommendation.j2`
2. **Pass 2 (Citations API):** Each knowledge item sent as `document` block with `citations: {"enabled": true}`. Returns reasoning chain with IDD phase titles, verified verbatim quotes, and evidence. Prompt: `backend/app/prompts/evidence_analysis.j2`

Reasoning steps are assigned IDD phase titles (Behovsanalys, Lämplighetsbedömning, Kostnadsinformation, etc.). Native citations are API-verified verbatim quotes. Deterministic services compute all numbers before the LLM call.

## Reasoning Trail

The reasoning chain is a first-class compliance record:
- Each step has a title, description, cited texts, conclusion
- Advisors can annotate individual steps (stored with author + timestamp)
- Compliance reviewers sign off on the entire chain
- Document generation renders the chain as the suitability assessment (titles, quotes, annotations)
- `reasoning_metadata` tracks review status: generated → pending_review → reviewed

## Firm Memory

Advisor insights (`FirmInsight` model) capture institutional knowledge:
- Scoped by case_type, collective_agreement, client_organization_id
- Categories: client_specific, product_tip, process_note, compliance_tip, lesson_learned, general
- `GET /relevant?case_id=uuid` returns insights matching a case's context (ranked by specificity)
- Surfaced in a "Firmans insikter" panel on the case detail page
- Post-case completion prompt encourages knowledge capture

## Knowledge Base

Real Swedish pension documents live in `backend/data/knowledge/`. Each PDF/TXT has a sidecar `.meta.json` with title, category, source, and tags. The seed script auto-ingests these into the database as chunked `KnowledgeItem` entries. Index: `backend/data/knowledge/document-index.json`.

## Dev Auth Bypass

In debug mode, the backend accepts `X-Dev-User-Id` and `X-Dev-Org-Id` headers instead of JWT tokens. The frontend sends these automatically from `.env.local`. Seed data IDs are deterministic.

## Domain Terminology

Use consistently:
- `case` (not ticket/request)
- `recommendation` (not suggestion/response)
- `evidence` (not reference)
- `audit_entry` (not log)
- `knowledge_item` (not document/chunk)
- `client_organization` (the employer company, not the advisory firm)
- `organization` (the advisory firm / tenant)
- `firm_insight` (advisor's institutional knowledge note)
- `suitability_assessment` (not compliance check — that's a different thing)
- `meeting_brief` (not prep/summary)
- `reasoning_trail` (the annotatable, reviewable reasoning chain)
