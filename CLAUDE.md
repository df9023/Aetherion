# CLAUDE.md — Aetherion Project Context for Claude Code

## What is Aetherion?

Aetherion (RetirementOS) is an AI-native decision workspace for pension, retirement, and long-term savings institutions. We help advisors, insurers, and pension operations teams reason through complex cases, generate compliant documentation, capture institutional knowledge, and execute workflows on top of legacy systems.

Starting market: Swedish occupational pension advisory workflows.

## Architecture

Monolithic FastAPI backend + Next.js frontend. PostgreSQL + pgvector for data and embeddings. See `docs/ARCHITECTURE_DECISIONS.md` for rationale on all major decisions.

**Frontend approach:** The initial Workbench UI is being prototyped in v0.dev (Vercel), then migrated into the repo as a Next.js app. Until migration, the frontend/ directory may be empty or minimal. Focus Claude Code efforts on the backend, API design, and ensuring API contracts are clean enough for the v0 prototype to consume.

## Five Modules

1. **Workbench** — advisor-facing case workspace (frontend-heavy)
2. **Reasoner** — LLM reasoning engine, structured outputs (backend: `services/reasoner.py`)
3. **Control** — compliance checks, audit trail (backend: `services/control.py`)
4. **Memory** — RAG over institutional knowledge (backend: `services/memory.py`)
5. **Flow** — workflow orchestration (backend: `services/flow.py`)

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
- Frontend: v0.dev (prototype) → Next.js 14+ / React / TypeScript / shadcn/ui / Tailwind (production)
- Database: PostgreSQL + pgvector
- LLM: Anthropic Claude API
- Auth: WorkOS
- Doc generation: python-docx, WeasyPrint, Jinja2
- Infra: Docker, Azure (EU-region)

## Common Commands

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Database
docker compose up db -d
alembic upgrade head

# Run tests
cd backend && pytest

# Frontend (after migration from v0)
# cd frontend && npm install && npm run dev
```

## Domain Terminology

Use these terms consistently:
- `case` (not ticket/request)
- `recommendation` (not suggestion/response)
- `evidence` (not reference)
- `audit_entry` (not log)
- `knowledge_item` (not document/chunk)
- `suitability_assessment` (not compliance check — that's a different thing)