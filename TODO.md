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

### Auth & Security
- [x] WorkOS integration (login, callback, logout, /me)
- [x] Rate limiting on LLM and auth endpoints (slowapi)
- [x] Security headers middleware
- [x] Startup validation for production secrets
- [x] Request logging middleware (non-PII)

### Native Citations (Two-Pass Architecture)
- [x] Refactored recommendation generation to two-pass: tool_use (structure) + Citations API (evidence)
- [x] Knowledge items sent as document blocks with `citations: {"enabled": true}`
- [x] Native citation parsing with document_index → knowledge_item_id mapping
- [x] Evidence model updated: cited_text, document_index, start/end_char_index, knowledge_item_id FK
- [x] Removed fuzzy CitationValidator — native citations are verified by definition
- [x] Frontend evidence cards show cited_text blockquotes
- [x] Migration 004_native_citations.py

### Codebase Cleanup
- [x] Removed unused prompt files
- [x] Updated CLAUDE.md, README.md, SETUP.md, TODO.md

### Knowledge Base — Document Ingestion
- [x] Document index created (`backend/data/knowledge/document-index.json`) with 24 Swedish pension documents
- [x] 24 `.meta.json` sidecar files generated for all documents
- [x] 9 of 11 direct PDFs downloaded into `backend/data/knowledge/`
- [x] Seed script auto-ingests PDFs with `.meta.json` sidecars (144 chunks from 9 documents)
- [x] RAG tested end-to-end: recommendation generation with native citations works

### Visual Redesign
- [x] v0 prototype generated (reference in `v0-reference/`)
- [x] v0 visual design applied to existing frontend (data layer intact)

### Bug Fixes
- [x] Fixed suitability score display (was showing "0.85 / 10 Low suitability" — now shows "85% High suitability")
- [x] Fixed document generation crash (LLM returns cost as string, DOCX formatter expected float)
- [x] Fixed database enum mismatch for `meeting_brief_generated`, `document_ingested`, `client_data_applied` audit actions

---

## In Progress

### Knowledge Base — Remaining Documents
- [ ] Download remaining 2 PDFs manually (PTK ITP2 guide, IDD directive from EUR-Lex)
- [ ] Save-as-PDF from browser for remaining 13 web pages (Pensionsmyndigheten, Skatteverket, minPension, etc.)
- [ ] Add InsureSec rules/guidelines and Lagen om försäkringsdistribution (2018:1219)
- [ ] Switch from hash-based embeddings to Voyage AI or OpenAI for real semantic search quality

### Git Cleanup
- [ ] Revoke leaked GitHub PAT (in `.cursor/mcp.json` git history)
- [ ] Remove `.cursor/mcp.json` from git tracking
- [ ] Delete stale `cursorrules` file (superseded by `CLAUDE.md`)
- [ ] Clean up or move `Aetherion.md` to `docs/`
- [ ] Remove `prompts/*.md` build prompts from tracking

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

### Auth & Security (remaining)
- [ ] Replace dev JWT stub with real WorkOS auth flow in frontend
- [ ] Role-based access control on all endpoints
- [ ] Directory sync (WorkOS)

---

## Post-Demo — Build After SPP Validation

### Product Catalog & Firm Offerings
> Different advisory firms (SPP, Max Matthiessen, Söderberg & Partners, etc.) have different distribution agreements, product shelves, and fee structures. Recommendations must be scoped to what the firm can actually offer — not generic advice.

- [ ] Domain model: `ProductOffering` entity (org-scoped) — provider, product name, category (traditional/unit-linked/hybrid), fee tiers, fund selection, transfer rules
- [ ] Domain model: `ProviderAgreement` entity — which insurance providers (Alecta, AMF, Folksam, Skandia, etc.) the org has distribution agreements with
- [ ] Seed data: SPP's actual product shelf as example
- [ ] Recommendation prompt receives org's available products as context — Claude recommends *from what the firm can sell*
- [ ] Cost disclosure (IDD section 7) uses the firm's actual fee schedule instead of generic estimates
- [ ] Conflict of interest disclosure (IDD section 8) reflects the firm's commission structure
- [ ] Frontend: org settings page for managing product catalog
- [ ] Frontend: recommendation shows which specific products were considered and why

### Scenario Modeling
- [ ] Scenario comparison mode: 2-3 parameter variations, side-by-side outcomes
- [ ] Frontend: interactive scenario builder with comparison cards

### Post-Meeting Follow-up
- [ ] Meeting notes input (manual or transcription)
- [ ] Auto-generate: client summary email (Swedish), internal notes, follow-up tasks

### Async Tasks
- [ ] Celery + Redis for background jobs
- [ ] Async document/recommendation generation

### Login & Onboarding
- [ ] Login page — polished, brand-forward landing page (WorkOS-powered auth)
- [ ] First-time setup flow for new organizations

### Organization Settings Page
- [ ] Sidebar: "Inställningar" page for the advisory firm
- [ ] Firm profile: name, org number, logo
- [ ] User management: invite/remove advisors, assign roles
- [ ] Product catalog configuration (ties into Product Catalog feature above)
- [ ] Branding/preferences

### Additional Sidebar Pages
- [ ] Dashboard / overview page (key metrics, recent activity, upcoming meetings)
- [ ] Reports page (compliance summaries, case throughput, advisor performance)
- [ ] Calendar / meeting schedule view

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
