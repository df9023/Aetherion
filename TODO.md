# Aetherion (Drident) — TODO

> **Product vision:** AI-native decision workspace for regulated pension advisory firms. Advisors manage cases, generate compliance-ready recommendations with verified citations, and produce IDD-compliant documentation. Three differentiating capabilities: Reasoning Trail, Firm Memory, Regulatory Pulse.

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
- [x] Full Swedish UI labels throughout all pages
- [x] UX overhaul: minimum text-xs, larger buttons, no fake elements, responsive layout

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

### Knowledge Base — Document Ingestion
- [x] Document index created (`backend/data/knowledge/document-index.json`) with 24 Swedish pension documents
- [x] 24 `.meta.json` sidecar files generated for all documents
- [x] 9 of 11 direct PDFs downloaded into `backend/data/knowledge/`
- [x] Seed script auto-ingests PDFs with `.meta.json` sidecars (144 chunks from 9 documents)
- [x] RAG tested end-to-end: recommendation generation with native citations works

### Deterministic Rules Engine
- [x] `SuitabilityEngine` — weighted rules-based scoring (risk match, age, income, agreement, data completeness)
- [x] `PensionCalculator` — ITP1/ITP2/SAF-LO/KAP-KL/AKAP-KL/PA16 rates, IBB lookup, salary exchange math
- [x] `EligibilityChecker` — collective agreement → provider mapping, recommendation type rules
- [x] 126 unit tests for all three services (pure, deterministic, no DB/async)

### Dashboard
- [x] `/dashboard` page — advisor home screen
- [x] Greeting header with time-of-day Swedish greeting + quick action buttons
- [x] Key metrics row (active cases, awaiting review, meetings this week, completed this month)
- [x] Cases needing attention (prioritized by urgency)
- [x] Recent activity feed (org-wide audit trail via `GET /api/v1/audit/recent`)
- [x] Upcoming meetings with prep status
- [x] Monthly performance stats
- [x] Sidebar: "Översikt" as first nav item

### Client Organizations
- [x] `ClientOrganization` model — employer companies the advisor manages (name, org number, industry, agreement, contacts)
- [x] FK from `Client` → `ClientOrganization` (optional, backward compatible)
- [x] Full CRUD endpoints at `/api/v1/client-organizations` with client count
- [x] Delete protection (409 when clients linked)
- [x] `/organizations` list page with search, create dialog, card grid
- [x] `/organizations/[id]` detail page with employee list + org info sidebar + edit dialog
- [x] Sidebar: "Organisationer" with Building2 icon
- [x] Client pages link to org when linked
- [x] Seed data: McKinsey Stockholm, Volvo Göteborg, Scandic Hotels
- [x] 9 tests (CRUD, client count, delete protection, org isolation)

### API Tests & Test Infrastructure
- [x] Async test infrastructure: conftest.py with DB fixtures, session-scoped event loop, header-based auth
- [x] Factory helpers in `tests/factories.py`
- [x] 42 async API tests: health, auth, cases, clients, knowledge, recommendations, dashboard
- [x] Multi-tenancy isolation tests (org2 can't see org1's data)
- [x] Total: 187+ tests, all passing in ~3 seconds

### Reasoning Trail (Drident Capability #1)
- [x] ReasoningStep expanded: title (IDD phases), cited_texts, advisor_annotation, annotated_by/at
- [x] `reasoning_metadata` JSONB column on Recommendation (total steps, annotated count, review status)
- [x] `PATCH /{id}/reasoning/{step}/annotate` — advisor annotation endpoint with audit entry
- [x] `POST /{id}/reasoning/review` — compliance sign-off with audit entry
- [x] Reasoner assigns IDD phase titles (Behovsanalys, Lämplighetsbedömning, Kostnadsinformation, etc.)
- [x] Document generation renders reasoning chain as compliance record (titles, cited blockquotes, annotations)
- [x] Frontend: expandable reasoning steps with inline annotation, review button, compliance badge
- [x] Backward compatible with old-format chains
- [x] 10 tests (annotation CRUD, review, audit entries, backward compat, org isolation)

### Firm Memory Phase 1 (Drident Capability #2)
- [x] `FirmInsight` model — org-scoped advisor insights with category, case type/agreement/client org scoping
- [x] `FirmInsightCategory` enum (client_specific, product_tip, process_note, compliance_tip, lesson_learned, general)
- [x] Full CRUD endpoints at `/api/v1/firm-insights` with filters (category, case_type, agreement, search)
- [x] `GET /relevant?case_id=uuid` — contextual matching: returns insights that match a case's context
- [x] Upvote endpoint
- [x] Frontend: "Firmans insikter" panel on case detail page with relevant insights
- [x] Frontend: `/insights` standalone page with filters, search, card grid
- [x] Sidebar: "Insikter" with Lightbulb icon
- [x] Post-case completion prompt encouraging knowledge capture
- [x] `INSIGHT_CREATED` audit action

### Visual Redesign & UX
- [x] v0 prototype generated (reference in `v0-reference/`)
- [x] v0 visual design applied to existing frontend
- [x] Global typography overhaul (min text-xs, removed text-[10px]/[11px])
- [x] Removed fake/non-functional elements (search bar, notification bell, hardcoded names)
- [x] Increased button and click target sizes throughout
- [x] Swedish labels for all UI text
- [x] Responsive layout on case detail page
- [x] Collapsible evidence section for progressive disclosure

### Bug Fixes
- [x] Fixed suitability score display (was showing "0.85 / 10 Low suitability" — now shows "85% High suitability")
- [x] Fixed document generation crash (LLM returns cost as string, DOCX formatter expected float)
- [x] Fixed database enum mismatch for `meeting_brief_generated`, `document_ingested`, `client_data_applied` audit actions

### Project Documentation
- [x] `drident.md` — product description, capabilities, privacy/security positioning
- [x] `drident-next-capabilities.md` — Regulatory Pulse, Reasoning Trail, Firm Memory specifications
- [x] `.cursor/rules/` — 7 focused Cursor rules (project, backend, frontend, security, testing, LLM, prompts)
- [x] `cursorrules` updated for enterprise SaaS vision

---

## In Progress

### Knowledge Base — Remaining Documents
- [ ] Download remaining 2 PDFs manually (PTK ITP2 guide, IDD directive from EUR-Lex)
- [ ] Save-as-PDF from browser for remaining 13 web pages (Pensionsmyndigheten, Skatteverket, minPension, etc.)
- [ ] Add InsureSec rules/guidelines and Lagen om försäkringsdistribution (2018:1219)
- [ ] Switch from hash-based embeddings to local HuggingFace model (KBLab/sentence-bert-swedish-cased)

### Git Cleanup
- [x] Revoked leaked GitHub PAT
- [ ] Remove `.cursor/mcp.json` from git tracking
- [ ] Clean up or move `Aetherion.md` to `docs/`
- [ ] Remove `prompts/*.md` build prompts from tracking

---

## Next Up

### Regulatory Pulse (Drident Capability #3)
> When regulations change, Drident traces the impact through the firm's active cases and tells advisors exactly what's affected.

- [ ] Regulatory change ingestion — new/updated knowledge items flagged as regulatory changes
- [ ] Dependency model: regulations ↔ case facts (case_type, collective_agreement, recommendation fields)
- [ ] Impact tracing: when a regulation changes, identify affected active cases
- [ ] Per-case impact flags with diff (old rule vs new rule, affected recommendation sections)
- [ ] Dashboard: "Regulatory Feed" showing recent changes with impact assessments
- [ ] "Compliance Health" view: cases current vs. cases with unresolved impacts
- [ ] Alerts (in-app) for high-severity changes affecting cases in review
- [ ] Firm Memory integration: check if patterns were based on changed rules

### Embeddings Upgrade
- [ ] Replace hash-based dev embeddings with local HuggingFace model (KBLab/sentence-bert-swedish-cased or intfloat/multilingual-e5-small)
- [ ] Add `sentence-transformers` + `torch` to requirements
- [ ] Update MemoryService embedding logic
- [ ] Re-embed all knowledge items

### Compliance Documentation Polish
- [ ] Review behovsanalys section against FI expectations
- [ ] Review lämplighetsbedömning section format
- [ ] Review kostnadsinformation section (total cost, impact on return)
- [ ] Separate behovsanalys document type (standalone)
- [ ] Separate lämplighetsbedömning document type (standalone)

### Knowledge Q&A (conversational)
- [ ] `POST /api/v1/knowledge/ask` — question in, grounded answer + sources out
- [ ] Frontend: Q&A chat interface in knowledge panel

### Auth & Security (remaining)
- [ ] Replace dev JWT stub with real WorkOS auth flow in frontend
- [ ] Role-based access control on all endpoints
- [ ] Directory sync (WorkOS)

---

## Post-Demo — Build After Validation

### Product Catalog & Firm Offerings
- [ ] `ProductOffering` entity (org-scoped) — provider, product name, category, fee tiers, fund selection
- [ ] `ProviderAgreement` entity — which providers the org has distribution agreements with
- [ ] Seed data: SPP's actual product shelf
- [ ] Recommendation prompt scoped to org's available products
- [ ] Cost disclosure uses firm's actual fee schedule
- [ ] Frontend: org settings page for managing product catalog

### Firm Memory Phase 2 — Pattern Detection
- [ ] Identify recurring patterns across completed cases (no individual client data)
- [ ] Surface patterns as suggestions that advisors validate or dismiss
- [ ] Confidence scoring — dismissed patterns fade, validated patterns strengthen

### Firm Memory Phase 3 — Recommendation Integration
- [ ] Validated firm patterns injected into recommendation prompts
- [ ] AI reasons with regulatory knowledge + firm's accumulated judgment

### Scenario Modeling
- [ ] Scenario comparison mode: 2-3 parameter variations, side-by-side outcomes
- [ ] Frontend: interactive scenario builder with comparison cards

### Post-Meeting Follow-up
- [ ] Meeting notes input (manual or transcription)
- [ ] Auto-generate: client summary email (Swedish), internal notes, follow-up tasks

### Login & Onboarding
- [ ] Login page — polished, brand-forward landing page
- [ ] First-time setup flow for new organizations

### Organization Settings Page
- [ ] Firm profile: name, org number, logo
- [ ] User management: invite/remove advisors, assign roles
- [ ] Product catalog configuration
- [ ] Branding/preferences

### Additional Pages
- [ ] Reports page (compliance summaries, case throughput, advisor performance)
- [ ] Calendar / meeting schedule view

### Production Readiness
- [ ] CI/CD via GitHub Actions (lint, test, build)
- [ ] Azure/Railway deployment (EU-region)
- [ ] Sentry for error monitoring
- [ ] PostHog for product analytics
- [ ] Managed PostgreSQL (Neon or Supabase)

### Advanced Testing
- [ ] LLM mock fixtures — deterministic Claude API responses for all tool schemas
- [ ] CI integration — tests run on every PR
- [ ] Service-layer unit tests (reasoner, control, memory, document, flow)
- [ ] Security tests (dev bypass blocked in prod, PII encryption verified, rate limiting)

---

## Competitive Context

| Competitor | Focus | What they don't do |
|---|---|---|
| **Conquest Planning** ($100M raised, 70% Canadian advisors) | US/CA/UK, deterministic calc engine, "compliance-first AI" | No Swedish pensions, no IDD docs, no RAG |
| **Wavvest** (founded 2024, Apex partnership) | US, AI financial planning co-pilot, custodial data | No European market, no pension-specific |
| **Zocks / Jump AI** | Meeting transcription + CRM automation | No reasoning engine, no compliance docs |

**Drident's edge**: Only product targeting European regulated pension advisory with IDD-compliant documentation, verified citations, deterministic calculations, and institutional knowledge capture (Firm Memory).
