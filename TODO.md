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

### Deterministic Rules Engine
> Principle: LLM should only generate narrative. Everything that can be computed — scores, costs, rates, eligibility — must be calculated in code. Compute first, narrate second.

**Suitability scoring (replace LLM-generated score):**
- [ ] `SuitabilityEngine` service — weighted rules-based scoring
- [ ] Factors: risk profile match, age appropriateness, income fit, agreement eligibility, investment horizon
- [ ] Each factor scored 0-1 with configurable weight, combined into final score
- [ ] Score + factor breakdown injected into LLM prompt as facts (LLM explains, doesn't score)

**Pension calculations (replace LLM-invented numbers):**
- [ ] `PensionCalculator` service — deterministic math for Swedish pension system
- [ ] Allmän pension: income pension + premium pension estimate based on income + age
- [ ] Tjänstepension contribution rates: ITP1 (4.5% ≤ 7.5 IBB, 30% above), SAF-LO (4.5%), AKAP-KR, PA16
- [ ] Salary exchange: tax savings = marginal rate × exchange amount
- [ ] Projected pension: capital × annuity factor (based on retirement age + life expectancy tables)
- [ ] IBB (inkomstbasbelopp) lookup table, updated yearly

**Cost calculations (replace LLM guesses):**
- [ ] Calculate from Product Catalog: total fee = platform fee + fund fee + insurance fee
- [ ] Cost impact on return: compound effect over investment horizon
- [ ] Scenario costs: deterministic diff between current and recommended product costs

**Eligibility rules:**
- [ ] Collective agreement → eligible providers/products (lookup table)
- [ ] Age → retirement window, early withdrawal rules
- [ ] Income thresholds for salary exchange viability

**Refactored LLM prompts:**
- [ ] Pass 1 prompt receives computed facts: suitability score, costs, pension estimates, eligibility
- [ ] LLM generates narrative summary, assumptions, and explanations around the facts
- [ ] LLM does NOT produce numbers — only explains the pre-computed numbers

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
> Stack: pytest + pytest-asyncio + httpx AsyncClient. Mock all LLM calls. Test database via Docker or SQLite.

**Test infrastructure:**
- [ ] `conftest.py` — test database setup, async session fixtures, test client factory
- [ ] `factories.py` — Factory functions for Organization, User, Client, Case, Recommendation
- [ ] LLM mock fixtures — deterministic Claude API responses for all tool schemas
- [ ] CI integration — tests run on every PR via GitHub Actions

**API endpoint tests (one test file per endpoint module):**
- [ ] `test_cases.py` — CRUD, status transitions, org isolation, invalid transitions rejected
- [ ] `test_clients.py` — CRUD, search, org isolation, PII encryption verified
- [ ] `test_recommendations.py` — generate, refine, evidence, document generation + download
- [ ] `test_knowledge.py` — CRUD, search, ingest, semantic search returns results
- [ ] `test_auth.py` — WorkOS flow, dev bypass only in debug mode, JWT validation
- [ ] `test_health.py` — health endpoint returns 200

**Service-layer unit tests:**
- [ ] `test_reasoner.py` — two-pass flow, structured output parsing, error handling, citation mapping
- [ ] `test_control.py` — all 5 compliance checks pass/fail correctly, audit entries created
- [ ] `test_memory.py` — embedding, search, chunking, knowledge CRUD
- [ ] `test_document.py` — DOCX generation, PDF generation, cost formatting, all 9 IDD sections
- [ ] `test_flow.py` — workflow step completion, pause/resume, state transitions
- [ ] `test_chunker.py` — document chunking produces expected chunk count and sizes

**Multi-tenancy tests:**
- [ ] Org A cannot see Org B's cases, clients, recommendations, knowledge
- [ ] All list endpoints return only org-scoped data
- [ ] Cross-org access returns 404, not 403 (no information leakage)

**Deterministic rules engine tests (when built):**
- [ ] `test_suitability.py` — known inputs → known score, each factor tested independently
- [ ] `test_pension_calc.py` — ITP1/SAF-LO/AKAP-KR rates verified against published values
- [ ] `test_cost_calc.py` — fee calculations match hand-computed expected values
- [ ] `test_eligibility.py` — agreement → provider mapping is correct

**Security tests:**
- [ ] Dev bypass blocked when DEBUG=false
- [ ] PII fields encrypted in database, decrypted on read
- [ ] Rate limiting enforced on LLM endpoints
- [ ] Invalid JWT returns 401
- [ ] Self-approval of own recommendation rejected

---

## Competitive Context

| Competitor | Focus | What they don't do |
|---|---|---|
| **Conquest Planning** ($100M raised, 70% Canadian advisors) | US/CA/UK, deterministic calc engine, "compliance-first AI" | No Swedish pensions, no IDD docs, no RAG |
| **Wavvest** (founded 2024, Apex partnership) | US, AI financial planning co-pilot, custodial data | No European market, no pension-specific |
| **Zocks / Jump AI** | Meeting transcription + CRM automation | No reasoning engine, no compliance docs |

**Aetherion's edge**: Only product targeting European regulated pension advisory with IDD-compliant documentation, Swedish occupational pension expertise, and institutional knowledge capture (Memory).
