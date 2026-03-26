# Aetherion — TODO

> **Demo goal (SPP):** An advisor opens the Workbench, preps for a client meeting with an auto-generated brief, clicks "Generate Recommendation", gets a structured IDD-compliant recommendation with full reasoning chain, then downloads the documentation pack. The wow moment is: "I just prepped a meeting in 2 minutes instead of 45."

---

## Done

### Backend Core
- [x] Domain models (Organization, User, Client, Case, Recommendation, Evidence, AuditEntry, KnowledgeItem, Document, Workflow)
- [x] Alembic migration with pgvector
- [x] CRUD API endpoints (cases, clients, recommendations, knowledge) — org-scoped
- [x] Multi-tenant isolation (organization_id on all entities)
- [x] PII encryption at rest (Fernet on client name, external_id)
- [x] Audit trail on every state change
- [x] Docker Compose (PostgreSQL with pgvector + Redis)
- [x] Seed script with realistic Swedish pension data (SPP as example org)

### Reasoner (Module 2) — AI Recommendation Engine
- [x] Reasoner with Claude tool_use for guaranteed structured output
- [x] `POST /api/v1/cases/{case_id}/generate-recommendation`
- [x] CaseType → RecommendationType inference
- [x] Optional additional_context from advisor
- [x] Recommendation refinement with version history (superseded tracking)
- [x] Client explanation generation (plain-language Swedish)

### Control (Module 3) — Compliance
- [x] Compliance checks (completeness, suitability, evidence, cost disclosure, conflict disclosure)
- [x] Self-approval prevention + role checks on recommendation approval
- [x] Document generation — recommendation packs (DOCX + PDF) with all 9 IDD compliance sections
- [x] `POST /api/v1/recommendations/{id}/generate-document`
- [x] `GET /api/v1/documents/{id}/download`

### Memory (Module 4) — Knowledge & RAG
- [x] OpenAI text-embedding-3-small integrated in MemoryService
- [x] Graceful fallback to hash-based embeddings when no API key
- [x] RAG retrieval returns semantically correct results
- [x] Knowledge CRUD + semantic search API

### Flow (Module 5) — Workflow
- [x] Flow service (workflow orchestration with step completion, pause/resume)
- [x] Pipeline test (end-to-end verification)

### Meeting Brief Generation
- [x] MEETING_BRIEF_TOOL (Claude tool_use schema)
- [x] meeting_brief.j2 Jinja2 prompt template (Swedish)
- [x] `POST /api/v1/cases/{case_id}/generate-brief`
- [x] Frontend: "Prepare Meeting" button with generating/generated states
- [x] Meeting brief viewer (pillar cards, severity badges, scenarios, agenda)

### Document Ingestion
- [x] DOCUMENT_EXTRACTION_TOOL (Claude tool_use schema with confidence scoring)
- [x] document_extraction.j2 Jinja2 prompt template (Swedish)
- [x] `POST /api/v1/clients/{id}/ingest-document` (PDF upload, text extraction, Claude vision fallback)
- [x] `POST /api/v1/clients/{id}/apply-extraction` (apply confirmed fields to client)
- [x] Frontend: document ingestion component (upload → extracting → review with confidence indicators)

### Frontend (Workbench UI)
- [x] Next.js 14 + shadcn/ui + Tailwind scaffolded
- [x] App shell (dark sidebar, top bar with breadcrumbs)
- [x] Cases list with search, status/type filters
- [x] Case detail with client info, meeting brief, AI recommendation, knowledge panel, audit trail
- [x] Document generation + download
- [x] Clients list with search
- [x] Client detail page with document ingestion and linked cases
- [x] Knowledge base page with category tabs
- [x] Create Client dialog + Create Case dialog
- [x] Case status transitions (dropdown with valid next states)
- [x] React Query hooks wired to all backend endpoints
- [x] Dev auth bypass (X-Dev-User-Id / X-Dev-Org-Id headers)

---

## In Progress

### Visual Redesign
- [ ] v0 prototype generated (reference in `v0-reference/`)
- [ ] Claude Code prompt ready (`prompts/claude-code-visual-redesign.md`)
- [ ] Apply v0 visual design to existing frontend (keep data layer intact)

---

## Next Up

### Compliance Documentation Polish
- [ ] Review behovsanalys section against FI expectations
- [ ] Review lämplighetsbedömning section format
- [ ] Review kostnadsinformation section (total cost, impact on return)
- [ ] Separate behovsanalys document type (standalone)
- [ ] Separate lämplighetsbedömning document type (standalone)

### Knowledge Q&A (conversational)
- [ ] `POST /api/v1/knowledge/ask` — question in, grounded answer + sources out
- [ ] Frontend: Q&A chat interface in knowledge panel (augment existing search)

### Auth & Security
- [ ] WorkOS integration (SSO, SAML, directory sync)
- [ ] Replace dev JWT stub with real auth flow
- [ ] Role-based access control on all endpoints
- [ ] Rate limiting on LLM endpoints

---

## Post-Demo — Build After SPP Validation

### Scenario Modeling
- [ ] Scenario comparison mode: 2-3 parameter variations, side-by-side outcomes
- [ ] Frontend: interactive scenario builder with comparison cards

### Post-Meeting Follow-up
- [ ] Meeting notes input (manual or transcription)
- [ ] Auto-generate: client summary email (Swedish), internal notes, follow-up tasks

### Async Tasks
- [ ] Celery + Redis for background jobs
- [ ] Async document/recommendation generation

### Production Readiness
- [ ] CI/CD via GitHub Actions (lint, test, build)
- [ ] Azure deployment (EU-region)
- [ ] Sentry for error monitoring
- [ ] PostHog for product analytics
- [ ] Neon or Supabase for managed PostgreSQL

### Testing
- [ ] pytest suite for all endpoints
- [ ] Service-layer unit tests
- [ ] Integration tests with test database

---

## Competitive Context

| Competitor | Focus | What they don't do |
|---|---|---|
| **Conquest Planning** ($100M raised, 70% Canadian advisors) | US/CA/UK, deterministic calc engine, "compliance-first AI" | No Swedish pensions, no IDD docs, no RAG |
| **Wavvest** (founded 2024, Apex partnership) | US, AI financial planning co-pilot, custodial data | No European market, no pension-specific |
| **Zocks / Jump AI** | Meeting transcription + CRM automation | No reasoning engine, no compliance docs |

**Aetherion's edge**: Only product targeting European regulated pension advisory with IDD-compliant documentation, Swedish occupational pension expertise, and institutional knowledge capture (Memory).
