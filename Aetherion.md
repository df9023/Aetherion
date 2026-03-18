# Aetherion — RetirementOS

> The AI operating system for retirement and pension decisions in regulated financial institutions.

---

## Mission

We exist because the world needs more high-quality retirement guidance than today's pension and insurance institutions can deliver. These firms still run critical decisions through fragmented manual workflows. We make expert retirement guidance scalable by automating the analysis, documentation, and compliance work around each case — so institutions can serve more people, faster, more consistently, and with more trust.

---

## What We're Building

An AI-native decision workspace for pension, retirement, and long-term savings institutions.

**One-liner:** We help pension providers, retirement advisors, and life insurers turn complex retirement cases into explainable recommendations, compliant documentation, and executable workflows.

### Target Users

- Pension advisors
- Workplace benefits consultants
- Retirement specialists
- Life insurers
- Wealth managers with retirement books
- Pension administrators
- Compliance and product teams

---

## Product Architecture

### 1. Workbench
The interface where advisors, specialists, and case handlers prepare, compare, explain, and execute retirement decisions.

### 2. Reasoner
The engine that shows *why* a recommendation was made, what assumptions were used, and what sources support it.

### 3. Control
The compliance and governance layer that makes every case auditable, reviewable, and approval-ready.

### 4. Memory
The institutional knowledge graph that captures product rules, precedent, internal playbooks, and expert decisions.

### 5. Flow
The orchestration layer that routes work, requests missing data, escalates exceptions, and syncs with core systems.

---

## Starting Wedge

**AI workspace for retirement casework and recommendation documentation.**

This means:
- Advisor prep and meeting briefings
- Retirement scenario generation and comparison
- Customer explanation drafts
- Suitability documentation
- Internal policy retrieval
- Evidence-backed recommendation packs
- Handoff into compliance / approval workflow

This wedge is global because every pension or retirement market has: product complexity, advice obligations, regulation, handoffs, and documentation burden.

---

## Go-to-Market

### Phase 1 — Sweden (PMF)
Starting with Swedish occupational pension and retirement-case workflows.

**Why Sweden:**
- Mature occupational pension usage
- Sophisticated institutional players
- Manageable market size for close iteration
- Strong trust and compliance requirements
- Enough complexity to prove the product

**Initial ICP:** Occupational pension advisors and intermediaries (fastest path to daily usage, strong pain around documentation and client communication).

**Target validation partners:** SPP, Max Matthiessen.

### Phase 2 — European Expansion
Expand through jurisdiction packs (regulatory rules, tax assumptions, product categories, disclosure requirements, pension structures, terminology).

### Phase 3 — Global
Layer market-specific integrations on top of the universal workflow layer.

---

## Expansion Model

### Layer 1: Universal Workflow Layer (reusable globally)
- Meeting prep
- Case summarization
- Recommendation drafting
- Internal knowledge search
- Explanation generation
- Evidence linking
- Approvals and handoffs

### Layer 2: Jurisdiction Packs (localized per market)
- Regulatory rules
- Tax assumptions
- Product categories
- Disclosure requirements
- Pension structures
- Terminology

### Layer 3: Market-Specific Integrations
- Pension admin systems
- CRM
- Insurer back ends
- Document systems
- Portfolio / reporting tools

---

## Competitive Landscape

| Player | What they do | Why we're different |
|---|---|---|
| Lumera | Life/pensions administration (Nordics) | We sit on top of admin systems, not replace them |
| minPension | Consumer pension overview | We solve institutional decision work, not consumer UX |
| Xaver | Digital distribution / embedded savings | Distribution-focused, not reasoning-workflow-focused |
| Generic LLM tools | General-purpose AI assistants | We encode retirement-specific reasoning + compliance |

**Whitespace:** AI-native operating layer for expert retirement work in regulated institutions.

---

## Tech Stack

### Environment
- **OS:** Linux via WSL (Ubuntu)
- **Project root:** `~/Aetherion`
- **AI credits:** YC Student AI Package

### Backend
- **Language:** Python 3.11+
- **Framework:** FastAPI (async, fast, great LLM ecosystem compatibility)
- **Task queue:** Celery + Redis (for async document generation, long-running LLM tasks)

### LLM / AI Layer
- **Orchestration:** Start with raw API calls (Anthropic Claude via YC package), layer in LangChain or LlamaIndex for RAG as needed
- **Embeddings:** OpenAI `text-embedding-3-small` or Cohere (evaluate cost vs quality)
- **RAG pipeline:** Retrieval-augmented generation over institutional docs, product rules, regulatory content

### Database
- **Primary:** PostgreSQL (case data, audit trails, user management, workflow state)
- **Vector store:** pgvector extension (embeddings for Memory module — keeps everything in one DB)
- **Cache / queue broker:** Redis

### Frontend
- **Framework:** Next.js (React + TypeScript)
- **UI components:** shadcn/ui + Tailwind CSS
- **State management:** Zustand or React Query

### Auth
- **Provider:** WorkOS (built for enterprise/regulated buyers — SSO, SAML, audit logs, directory sync)
- **Alternative:** Clerk or Auth0

### Document Generation
- **Word/PDF output:** python-docx, WeasyPrint
- **Templating:** Jinja2 for recommendation packs, compliance docs

### Infrastructure
- **Containers:** Docker from day one
- **Cloud:** Azure (strongest compliance story with European regulated financial institutions, EU-region hosting)
- **CI/CD:** GitHub Actions (keep it simple)
- **Monitoring:** Sentry (errors), PostHog (product analytics)

### What to Skip for Now
- Kubernetes (overkill until needed)
- Microservices (start monolithic, split later)
- Custom auth system
- Complex CI/CD pipelines

---

## Key Questions to Validate with Partners

1. Where do advisors / specialists spend the most non-client time?
2. What parts of retirement or occupational pension advice are hardest to document well?
3. Where do cases get delayed internally?
4. Which decisions require the most manual justification or compliance signoff?
5. What knowledge today lives mostly in senior people's heads?
6. What would have to be true for AI outputs to be trusted internally?
7. Which workflows would be valuable even without deep core-system integration?

---

## Thesis

Build a global AI operating system for retirement and pension decisions, starting with Swedish occupational pension and retirement-case workflows. The product helps advisors, insurers, and pension operations teams reason through complex cases, generate compliant documentation, capture institutional knowledge, and execute workflows on top of legacy systems.

---

## Key Risks

- **Go-to-market speed:** Can we get to daily usage fast enough to learn?
- **Jurisdiction portability:** Can Layer 2 (jurisdiction packs) scale without heavy consulting?
- **Knowledge bootstrapping:** Getting the first institution's playbooks, product rules, and precedent into the system fast enough to show value before a long onboarding kills the deal.
- **Platform risk:** Horizontal AI tools (Copilot, etc.) eating the "case prep and drafting" use case from above.
- **Incumbent response:** Pension admin systems adding their own AI layers.

**Defensibility comes from:** Depth in retirement-specific reasoning, compliance-grade outputs, and institutional knowledge capture (Reasoner + Control + Memory).