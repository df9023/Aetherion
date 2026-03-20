# Aetherion — TODO

> **Demo goal (SPP):** An advisor opens the Workbench, preps for a client meeting with an auto-generated brief, clicks "Generate Recommendation", gets a structured IDD-compliant recommendation with full reasoning chain, then downloads the documentation pack. The wow moment is: "I just prepped a meeting in 2 minutes instead of 45."

---

## Done

### Backend Core
- [x] Domain models (Organization, User, Client, Case, Recommendation, Evidence, AuditEntry, KnowledgeItem, Document, Workflow)
- [x] Alembic migration with pgvector
- [x] CRUD API endpoints (cases, clients, recommendations, knowledge) — org-scoped
- [x] Multi-tenant isolation (organization_id on all entities including Client)
- [x] PII encryption at rest (Fernet on client name, external_id)
- [x] Audit trail on every state change
- [x] Docker Compose (PostgreSQL with pgvector + Redis)
- [x] Seed script with realistic Swedish pension data (SPP as example org)
- [x] ValueEnum helper for PostgreSQL enum compatibility

### Reasoner (Module 2) — AI Recommendation Engine
- [x] Reasoner with Claude tool_use for guaranteed structured output
- [x] `POST /api/v1/cases/{case_id}/generate-recommendation` (core product loop)
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
- [x] OpenAI `text-embedding-3-small` integrated in MemoryService
- [x] Graceful fallback to hash-based embeddings when no API key
- [x] RAG retrieval returns semantically correct results
- [x] Knowledge CRUD + semantic search API

### Flow (Module 5) — Workflow
- [x] Flow service (workflow orchestration with step completion, pause/resume)
- [x] Pipeline test (end-to-end verification)

### Frontend (Workbench UI)
- [x] Next.js 14 + shadcn/ui + Tailwind scaffolded
- [x] App shell (dark sidebar, top bar with breadcrumbs)
- [x] Cases list with search, status/type filters
- [x] Case detail with client info, AI recommendation (generate, reasoning chain, evidence, scenarios, suitability score)
- [x] "Generate Recommendation" button → calls AI endpoint
- [x] Document generation + download
- [x] Knowledge search panel in case detail
- [x] Audit trail timeline
- [x] Clients list with search
- [x] Client detail page with linked cases
- [x] Knowledge base page with category tabs
- [x] Create Client dialog (full form)
- [x] Create Case dialog (client selector, redirects to new case)
- [x] Case status transitions (dropdown with valid next states)
- [x] Real breadcrumbs (API-driven, not mock data)
- [x] React Query hooks wired to all backend endpoints
- [x] Global error handling (toast on mutation errors)
- [x] Dev auth bypass (X-Dev-User-Id / X-Dev-Org-Id headers)

---

## SPP Demo — Must Have (Priority 1-3)

### 1. Case Prep / Meeting Brief Generation ← **THE WOW MOMENT**
> *"This is the single most requested feature across the industry."*
> Conquest, Zocks, Wavvest all attack this. For pension advisors: pull the client's full situation, identify gaps, pre-generate scenarios, have a draft agenda ready.

- [ ] **New endpoint**: `POST /api/v1/cases/{case_id}/generate-brief`
  - Takes client data + case context
  - Calls Claude to generate a structured meeting brief
  - Output: pension overview across all three pillars (allmän, tjänste, privat), key issues flagged, pre-modeled scenarios, talking points, suggested agenda
- [ ] **Pydantic schema** for `MeetingBrief` — structured output with sections:
  - Client overview (age, employer, agreement, income, years to retirement)
  - Pension situation summary (current holdings per pillar, projected outcomes)
  - Key issues & gaps identified
  - Pre-modeled scenarios (retirement age variations, salary exchange options)
  - Talking points / agenda items
  - Open questions for the client
- [ ] **Jinja2 prompt template** in `backend/app/prompts/meeting_brief.j2`
- [ ] **Frontend: "Prepare Meeting" button** on case detail page
  - Shows generating state → then renders the brief in a clean, printable card layout
  - Option to download as PDF (reuse DocumentService)
- [ ] **Frontend: Meeting brief viewer** — expandable sections matching the schema
- [ ] Store generated brief on the case (new field or as a document)

### 2. Recommendation with Full Reasoning Chain — DONE
- [x] Already built and working end-to-end
- [ ] **Polish**: Ensure the output format matches what Swedish compliance teams expect
  - [ ] Review behovsanalys section against FI expectations
  - [ ] Review lämplighetsbedömning section format
  - [ ] Review kostnadsinformation section (total cost, impact on return)

### 3. Compliance Documentation Output — DONE (polish needed)
- [x] 9-section recommendation pack generated
- [ ] **Polish**: Validate output with someone who's seen real FI-reviewed documentation
- [ ] **Add**: Separate behovsanalys document type (needs analysis as standalone doc)
- [ ] **Add**: Separate lämplighetsbedömning document type (suitability assessment as standalone)

---

## SPP Demo — Should Have (Priority 4-5)

### 4. Knowledge Retrieval — Natural Language Q&A
> *"Pension advisors constantly need to look up product rules, internal policies, fee structures."*
> Conquest's SAM Guide does this. Your Memory module is already specced and partly built.

- [x] Semantic search works (POST /knowledge/search)
- [x] Knowledge panel in case detail
- [ ] **Upgrade to conversational Q&A**: advisor types a question → Memory retrieves context → Claude generates a direct answer with source citations
  - New endpoint: `POST /api/v1/knowledge/ask`
  - Input: `{ question: string }`
  - Output: `{ answer: string, sources: KnowledgeItem[] }`
  - Uses RAG: embed question → retrieve top-k → Claude answers grounded in retrieved context
- [ ] **Frontend**: Replace or augment the knowledge search panel with a Q&A chat interface
  - Show the answer with inline source references
  - Keep the list view as a fallback/browse mode

### 5. Document Ingestion — Upload & Extract
> *"Upload a PDF pension statement → auto-extract data → populate client profile. This alone saves 20-30 minutes per case."*
> Conquest's LLM Data Migration, RightCapital's Smart Import — both getting massive traction.

- [ ] **New endpoint**: `POST /api/v1/clients/{client_id}/ingest-document`
  - Accepts PDF/image upload (pensionsbesked, lönespecifikation, insurance policy)
  - Uses Claude vision or text extraction to parse the document
  - Returns structured data: pension holdings, provider, fees, coverage details
  - Optionally auto-updates client profile fields
- [ ] **Pydantic schema** for extracted pension data
- [ ] **Frontend**: Upload button on client detail page
  - Drag-and-drop or file picker
  - Shows extraction results for advisor review before confirming
  - "Accept & Update Profile" button to apply extracted data

---

## Post-Demo — Build After SPP Validation

### Scenario Modeling (Medium Priority)
> *Collapse multi-step scenario modeling into single workflows.*

- [ ] Scenario comparison mode: input 2-3 parameter variations, get side-by-side outcomes
- [ ] Parameters: retirement age, withdrawal sequence, salary exchange amounts, fund allocation
- [ ] Frontend: interactive scenario builder with comparison cards

### Post-Meeting Follow-up (Lower Priority)
> *Auto-generate: summary email to client, internal notes, follow-up tasks, next review date.*

- [ ] Meeting notes input (manual or transcription)
- [ ] Auto-generate: client summary email (Swedish), internal case notes, follow-up tasks
- [ ] Wire into Flow module for task tracking

### Auth & Security
- [ ] WorkOS integration (SSO, SAML, directory sync)
- [ ] Replace dev JWT stub with real auth flow
- [ ] Role-based access control on all endpoints

### Async Tasks
- [ ] Celery + Redis for background jobs
- [ ] Async document generation
- [ ] Async recommendation generation (for long-running cases)

### Workflow Endpoints
- [ ] Expose FlowService via API
- [ ] Wire workflow status to case status transitions
- [ ] UI for workflow progress tracking

### Testing
- [ ] pytest suite for all endpoints
- [ ] Service-layer unit tests (Reasoner, Control, Memory, Flow)
- [ ] Integration tests with test database

### Production Readiness
- [ ] CI/CD via GitHub Actions (lint, test, build)
- [ ] Azure deployment (EU-region)
- [ ] Sentry for error monitoring
- [ ] PostHog for product analytics
- [ ] Rate limiting on LLM endpoints
- [ ] Request logging (non-PII)
- [ ] Neon or Supabase for managed PostgreSQL

---

## Competitive Context

| Competitor | Focus | What they don't do |
|---|---|---|
| **Conquest Planning** ($100M raised, 70% Canadian advisors) | US/CA/UK, deterministic calc engine, "compliance-first AI" | No Swedish pensions, no IDD docs, no RAG |
| **Wavvest** (founded 2024, Apex partnership) | US, AI financial planning co-pilot, custodial data | No European market, no pension-specific |
| **Zocks / Jump AI** | Meeting transcription + CRM automation | No reasoning engine, no compliance docs |

**Aetherion's edge**: Only product targeting European regulated pension advisory with IDD-compliant documentation, Swedish occupational pension expertise, and institutional knowledge capture (Memory).
