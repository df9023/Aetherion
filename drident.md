# Drident

**AI-native decision workspace for pension advisory teams.**

---

## The Problem

Swedish pension advisors spend 60-70% of their time on administrative work — gathering client data, cross-referencing regulations, writing compliant recommendation documents, and preparing for meetings. The actual advisory work — understanding a client's situation and recommending the right path — gets squeezed into whatever time is left.

Meanwhile, compliance requirements keep growing. IDD demands full suitability assessments, cost disclosures, and conflict-of-interest documentation for every recommendation. Finansinspektionen expects structured needs analyses. Every decision must be auditable. Advisors are buried in paperwork, and firms are exposed to regulatory risk when corners get cut.

Existing tools are either generic CRMs that don't understand pension, or rigid legacy systems that force advisors into box-ticking workflows.

## What Drident Does

Drident is a workspace where an advisor manages their entire caseload — from the first client meeting to the signed recommendation pack. AI handles the heavy lifting; the advisor stays in control.

**Core workflow:**

1. An advisor opens a case for a client — say, Anna Johansson at McKinsey Stockholm needs a pension review.
2. Drident pulls in what it knows: her employment, collective agreement (ITP1), income, risk profile. Documents can be uploaded and automatically parsed.
3. The advisor hits "Generate Recommendation." Drident's reasoning engine analyzes the case against the firm's knowledge base — Swedish pension regulations, product rules, internal policies — and produces a structured recommendation with exact citations from source documents.
4. Every number in the recommendation is computed deterministically — pension contributions, suitability scores, salary exchange calculations — not invented by the AI. The AI explains the numbers; it doesn't make them up.
5. The advisor reviews, refines if needed, and downloads a complete IDD-compliant recommendation pack (PDF or Word) with all nine required sections: needs analysis, suitability assessment, cost disclosure, conflict of interest, and more.
6. Every action is logged in an immutable audit trail. Compliance can review any case end-to-end.

## Key Capabilities

### Recommendation Engine

Two-pass AI architecture: structured output for the recommendation, then a separate citation pass that guarantees every quote is verbatim from the source document. No hallucinated references. Every piece of evidence links back to a real regulation or policy with exact text.

### Deterministic Calculations

Pension math (ITP1, ITP2, SAF-LO, KAP-KL, AKAP-KL, PA16 contribution rates), suitability scoring (weighted multi-factor), eligibility checks (collective agreement to provider mapping), and salary exchange calculations — all computed in code, not by the LLM. The AI reasons around verified facts.

### Knowledge Base

RAG-powered retrieval over the firm's regulatory corpus — Finansinspektionen rules, IDD implementation guidelines, Pensionsmyndigheten guidance, internal policies. Documents are chunked, embedded, and searchable. Citations are API-verified, not fuzzy-matched.

### Client Organization Management

Advisors manage their portfolio of employer clients (McKinsey, Volvo, Scandic) — see all employees, their cases, collective agreements, and HR contacts in one place. The organizational structure mirrors how advisory firms actually work: advisor owns the company relationship, advises individual employees within it.

### Meeting Preparation

One-click meeting briefs that synthesize the client's situation, open issues, regulatory considerations, and suggested talking points. The advisor walks into every meeting prepared.

### Document Generation

IDD-compliant recommendation packs generated automatically — needs analysis, suitability assessment, cost information, product comparisons, conflict disclosure. Output as PDF or Word. The advisor reviews and signs; they don't write from scratch.

### Compliance & Audit

Every case state change, every recommendation generated, every document produced — logged with timestamp, actor, and context. Full audit trail for internal compliance review and regulatory inspection.

### Dashboard

Advisor home screen: active cases, cases awaiting review, upcoming meetings, recent activity across the portfolio, monthly performance. The advisor sees what needs attention without digging through individual cases.

## Who It's For

**Today:** Swedish occupational pension advisory firms — independent advisors, insurance brokers, and pension consultants who advise employees on tjänstepension, salary exchange, and retirement planning.

**Tomorrow:** Any regulated financial advisory workflow where compliance documentation, institutional knowledge, and structured reasoning matter — life insurance, wealth management, benefits consulting.

## What's Built

- Full case management lifecycle (draft → preparation → review → approval → completed)
- AI recommendation generation with native citations
- Deterministic calculation engine (pension, suitability, eligibility)
- Knowledge base with document ingestion and semantic search
- Client organization management
- Meeting preparation automation
- IDD-compliant document generation (PDF + DOCX)
- Immutable audit trail
- Multi-tenant architecture (org-scoped data isolation)
- Advisor dashboard
- WorkOS authentication integration
- PII encryption at rest
- Rate limiting on AI endpoints
- 177+ automated tests (unit + API + multi-tenancy isolation)

## Privacy, Security & Compliance

### Data Architecture

- Client data lives in **the firm's own database** — Drident controls what gets sent to the LLM and when
- Only **relevant document chunks** are sent per query — not the full client profile or knowledge base
- **PII is encrypted at rest** and can be stripped/anonymized before any LLM call
- **Deterministic calculations** (pension math, suitability scores) never touch the LLM — sensitive numbers stay in code
- Full **audit trail** of every LLM interaction — what was sent, what came back, when, by whom

### Deployment Options

| Tier | How it works | For whom |
|------|-------------|----------|
| **API + DPA** | Anthropic or Azure OpenAI with enterprise Data Processing Agreement. No training on your data, data deleted after processing. Azure runs in EU (Sweden Central). | Most firms |
| **Private deployment** | LLM runs inside the firm's own Azure/AWS tenant via private endpoints. Data never leaves their cloud boundary. | Regulated firms |
| **On-premise** | Self-hosted open-source models + local Swedish embedding model. Complete data sovereignty. | Maximum control |

### Regulatory Alignment

- **GDPR Article 28** — DPA with LLM provider. Drident acts as the data controller's processor.
- **EU AI Act** — Decision-support tool with human-in-the-loop. Advisor reviews and approves every recommendation.
- **Finansinspektionen (FFFS 2014:1)** — Azure Sweden Central keeps data processing within Swedish jurisdiction.
- **IDD** — Generates required documentation structure. Audit trail proves the process was followed.

### Why Not Just Use Copilot?

| | Copilot | Drident |
|---|---|---|
| Domain knowledge | Generic | Swedish pension regulations, IDD, FI rules built in |
| Citations | Unverified | API-verified verbatim quotes from source documents |
| Calculations | LLM-generated | Deterministic — computed in code, not hallucinated |
| Compliance | No audit trail | Full audit trail, IDD-compliant document generation |
| Data control | Microsoft's infrastructure | You choose: API, private cloud, or on-premise |

*"Your advisors are already using ChatGPT — you just don't know about it. Drident gives them something better and gives you control over it."*

## What's Next

- **Product Catalog** — each firm's available products and provider agreements, so recommendations match what the firm can actually sell
- **Login & onboarding** — polished entry experience, firm setup flow
- **Local embeddings** — Swedish-tuned model (KBLab) for semantic search, eliminating external API dependency
- **Scenario modeling** — side-by-side comparison of 2-3 pension scenarios
- **Post-meeting follow-up** — auto-generated client summary emails and internal notes
- **Reports** — compliance summaries, case throughput, advisor performance
- **Production deployment** — CI/CD, monitoring, managed database, EU-region hosting

---

*Drident doesn't replace the advisor. It removes everything that gets in the way of advising.*
