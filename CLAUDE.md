# CLAUDE.md — Aetherion Project Context for Claude Code

## What is Aetherion?

Aetherion is an AI-native decision workspace for pension, retirement, and long-term savings institutions. We help advisors, insurers, and pension operations teams reason through complex cases, generate compliant documentation, capture institutional knowledge, and execute workflows on top of legacy systems.

Starting market: Swedish occupational pension advisory workflows. Example org in dev: **SPP**.

## Architecture

Monolithic FastAPI backend + Next.js 14 frontend. PostgreSQL + pgvector for data and embeddings.

See `docs/ARCHITECTURE_DECISIONS.md` for rationale on all major decisions.

## Five Modules

1. **Workbench** — advisor-facing case workspace (`frontend/`)
2. **Reasoner** — LLM reasoning engine, two-pass: tool_use for structured fields + Citations API for verified evidence (`backend/app/services/reasoner.py`)
3. **Control** — compliance checks, audit trail, IDD-compliant document generation (`backend/app/services/control.py`, `backend/app/services/document.py`)
4. **Memory** — RAG over institutional knowledge with pgvector, document ingestion pipeline (`backend/app/services/memory.py`)
5. **Flow** — workflow orchestration (`backend/app/services/flow.py`)

## Key Reference Documents

Read these BEFORE building features in these areas:

- `docs/DOMAIN_MODEL.md` — all data entities, relationships, and design principles
- `docs/RAG_PIPELINE.md` — Memory module ingestion, chunking, embedding, retrieval
- `docs/COMPLIANCE_SPEC.md` — recommendation pack structure, audit trail requirements, compliance checks
- `docs/ARCHITECTURE_DECISIONS.md` — ADRs explaining why things are built the way they are

## Coding Standards

- Python: type hints everywhere, Pydantic for all schemas, async endpoints, service layer pattern
- TypeScript: strict mode, no `any`, functional components, React Query for server state
- All LLM prompts in `backend/app/prompts/` as Jinja2 templates, never hardcoded
- All LLM outputs parsed into Pydantic models, never stored as raw text
- Every case/recommendation state change creates an AuditEntry
- Multi-tenant: always scope queries by organization_id
- Never log PII in plaintext

## Tech Stack

- Backend: Python 3.11+ / FastAPI
- Frontend: Next.js 14 / React / TypeScript / shadcn/ui (New York) / Tailwind CSS
- Database: PostgreSQL 16 + pgvector
- LLM: Anthropic Claude API — two-pass architecture: tool_use (structured output) + Citations API (verified evidence)
- Embeddings: Voyage AI voyage-3 (primary) or OpenAI text-embedding-3-small (fallback); hash-based fake embeddings in dev without API keys
- Auth: WorkOS (backend integrated: login, callback, logout, /me), dev bypass via X-Dev-User-Id / X-Dev-Org-Id headers
- Doc generation: python-docx, WeasyPrint, Jinja2
- PDF extraction: pdfplumber
- Infra: Docker Compose (dev), Azure EU-region (prod, planned)

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
python -m scripts.seed               # Seed dev data (SPP org, users, clients, cases, knowledge docs)

# Frontend
cd frontend
npm install
npm run dev                          # http://localhost:3000

# Tests
cd backend && pytest
```

## Key Backend Endpoints

- `POST /api/v1/cases/{id}/generate-recommendation` — AI recommendation with reasoning chain
- `POST /api/v1/cases/{id}/generate-brief` — Meeting brief generation
- `POST /api/v1/recommendations/{id}/generate-document` — Compliance doc (DOCX/PDF)
- `GET /api/v1/documents/{id}/download` — Download generated document
- `POST /api/v1/clients/{id}/ingest-document` — PDF upload + AI data extraction
- `POST /api/v1/clients/{id}/apply-extraction` — Apply extracted data to client profile
- `POST /api/v1/knowledge/search` — Semantic search over knowledge base

## Frontend Data Layer

- API client: `frontend/lib/api.ts` (apiFetch, apiUpload, apiDownload with dev auth headers)
- React Query hooks: `frontend/lib/hooks.ts` (all backend endpoints wired)
- UI labels/styles: `frontend/lib/labels.ts`
- Providers: `frontend/components/providers.tsx` (QueryClientProvider)

## Two-Pass Recommendation Architecture

Recommendation generation uses two sequential LLM calls:

1. **Pass 1 (tool_use):** Returns structured fields — summary, assumptions, scenarios, suitability_score, cost_disclosure, conflict_disclosure. Prompt: `backend/app/prompts/recommendation.j2`
2. **Pass 2 (Citations API):** Each knowledge item is sent as a `document` content block with `citations: {"enabled": true}`. Returns reasoning chain with verified verbatim quotes and evidence with exact source references. Prompt: `backend/app/prompts/evidence_analysis.j2`

Native citations are verified by definition (the API guarantees `cited_text` is extracted verbatim from the source document). No fuzzy matching needed.

## Knowledge Base

Real Swedish pension documents live in `backend/data/knowledge/`. Each PDF/TXT has a sidecar `.meta.json` with title, category, source, and tags. The seed script auto-ingests these into the database as chunked `KnowledgeItem` entries. Index of all documents: `backend/data/knowledge/document-index.json`.

## Dev Auth Bypass

In debug mode, the backend accepts `X-Dev-User-Id` and `X-Dev-Org-Id` headers instead of JWT tokens. The frontend sends these automatically from `.env.local`. Seed data IDs are deterministic.

## Domain Terminology

Use these terms consistently:
- `case` (not ticket/request)
- `recommendation` (not suggestion/response)
- `evidence` (not reference)
- `audit_entry` (not log)
- `knowledge_item` (not document/chunk)
- `suitability_assessment` (not compliance check — that's a different thing)
- `meeting_brief` (not prep/summary)
