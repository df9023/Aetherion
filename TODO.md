# Aetherion — TODO

> **Demo goal:** An advisor opens the Workbench, selects a client case, clicks "Generate Recommendation", and within seconds gets a structured, evidence-backed pension recommendation with reasoning chain, suitability score, cost disclosures, and a downloadable Swedish-language recommendation pack.
>
> Get there and we have something to demo to SPP / Max Matthiessen.

---

## Done

- [x] Domain models (Organization, User, Client, Case, Recommendation, Evidence, AuditEntry, KnowledgeItem, Document, Workflow)
- [x] Alembic migration with pgvector
- [x] CRUD API endpoints (cases, clients, recommendations, knowledge) — org-scoped
- [x] Multi-tenant isolation (organization_id on all entities including Client)
- [x] PII encryption at rest (Fernet on client name, external_id)
- [x] Audit trail on every state change
- [x] Compliance checks (completeness, suitability, evidence, cost disclosure, conflict disclosure)
- [x] Reasoner with Claude tool_use for guaranteed structured output
- [x] Client explanation generation (plain-language Swedish)
- [x] Recommendation refinement with version history (superseded tracking)
- [x] Flow service (workflow orchestration with step completion, pause/resume)
- [x] Seed script with realistic Swedish pension data (ITP1/ITP2 clients, 6 knowledge items)
- [x] Pipeline test (end-to-end verification)
- [x] ValueEnum helper for PostgreSQL enum compatibility
- [x] Self-approval prevention + role checks on recommendation approval
- [x] Docker Compose (PostgreSQL with pgvector + Redis)
- [x] Real embeddings via OpenAI text-embedding-3-small (with hash-based fallback)
- [x] AI generate endpoint — `POST /cases/{case_id}/generate-recommendation` (core product loop)
- [x] Document generation — recommendation packs (DOCX + PDF) with all 9 compliance sections

---

## Next — Path to Demo

### ~~1. Real embeddings (Memory module)~~ Done
- [x] OpenAI `text-embedding-3-small` integrated in MemoryService
- [x] Graceful fallback to hash-based embeddings when no API key
- [x] Seed script uses real embeddings when available
- [x] RAG retrieval returns semantically correct results

### ~~2. "Generate with AI" endpoint~~ Done
- [x] `POST /api/v1/cases/{case_id}/generate-recommendation`
- [x] Loads case + client, retrieves knowledge via MemoryService, calls ReasonerService
- [x] CaseType → RecommendationType inference
- [x] Optional additional_context from advisor
- [x] Pipeline test updated

### ~~3. Document generation (recommendation packs)~~ Done
- [x] DocumentService with DOCX + PDF generation
- [x] 9-section Jinja2 HTML template (all Swedish, per COMPLIANCE_SPEC.md)
- [x] `POST /api/v1/recommendations/{id}/generate-document`
- [x] `GET /api/v1/documents/{id}/download`
- [x] AuditEntry on generation, files stored in `generated_documents/`

### 4. Frontend (Workbench UI) ← **You are here**
- [ ] Migrate v0.dev prototype into `frontend/` (Next.js + shadcn/ui + Tailwind)
- [ ] Case list / dashboard
- [ ] Case detail view with client info
- [ ] "Generate Recommendation" button → calls the AI endpoint
- [ ] Recommendation viewer (reasoning chain, evidence, scenarios, suitability score)
- [ ] "Download as PDF" button
- [ ] Knowledge search panel

---

## Later — Post-Demo

### Auth
- [ ] WorkOS integration (SSO, SAML, directory sync)
- [ ] Replace dev JWT stub with real auth flow
- [ ] Role-based access control on all endpoints

### Async tasks
- [ ] Celery + Redis for background jobs
- [ ] Async document generation
- [ ] Async recommendation generation (for long-running cases)

### Workflow endpoints
- [ ] Expose FlowService via API (`POST /workflows`, `POST /workflows/{id}/complete-step`, etc.)
- [ ] Wire workflow status to case status transitions
- [ ] UI for workflow progress tracking

### Testing
- [ ] pytest suite for all endpoints
- [ ] Service-layer unit tests (Reasoner, Control, Memory, Flow)
- [ ] Integration tests with test database

### Production readiness
- [ ] CI/CD via GitHub Actions (lint, test, build)
- [ ] Azure deployment (EU-region)
- [ ] Sentry for error monitoring
- [ ] PostHog for product analytics
- [ ] Rate limiting on LLM endpoints
- [ ] Request logging (non-PII)
