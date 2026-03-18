# Architecture Decision Records

This document captures key architectural decisions for Aetherion. When building features, check here first to understand *why* things are the way they are.

---

## ADR-001: Monolith-First Architecture

**Decision:** Start with a monolithic FastAPI backend, not microservices.

**Context:** Early-stage product with a single developer. Need to iterate fast, change data models frequently, and avoid operational overhead.

**Rationale:**
- One deployment target, one database, one codebase to reason about
- Service boundaries aren't clear yet — premature splitting creates wrong abstractions
- FastAPI's router system provides logical separation without physical separation
- Can extract services later when we understand the actual bottlenecks

**Consequences:** All five modules (Workbench, Reasoner, Control, Memory, Flow) live in the same process. Separate them at the service layer (different service files), not at the infrastructure layer.

---

## ADR-002: PostgreSQL + pgvector Over Dedicated Vector DB

**Decision:** Use PostgreSQL with the pgvector extension for both relational data and vector embeddings, rather than a separate vector database like Pinecone or Weaviate.

**Context:** Need to store case data, audit trails, user records (relational) AND knowledge embeddings (vector). Two databases means two things to manage, sync, and pay for.

**Rationale:**
- One database to operate, back up, and reason about
- pgvector performance is sufficient for our scale (thousands to low millions of vectors)
- Transactional consistency — can update a knowledge item and its embedding atomically
- Reduces infrastructure cost and complexity
- HNSW indexing in pgvector provides fast approximate nearest neighbor search

**When to revisit:** If retrieval latency becomes a bottleneck at >1M vectors, or if we need advanced vector DB features (hybrid search, filtering at scale). Unlikely in the first 1-2 years.

---

## ADR-003: WorkOS for Authentication

**Decision:** Use WorkOS for authentication and identity, not Clerk, Auth0, or custom auth.

**Context:** Selling to regulated financial institutions. They require SSO (SAML/OIDC), directory sync, and audit logs. Building this ourselves would take months.

**Rationale:**
- WorkOS is purpose-built for enterprise auth with regulated buyers
- SAML SSO and directory sync out of the box
- Audit log API for compliance requirements
- Admin portal that IT teams at pension companies can self-manage
- Reasonable pricing for early stage

**Consequences:** User management flows through WorkOS. Our User model stores a `workos_user_id` reference. Role-based access control logic lives in our app, but authentication is delegated.

---

## ADR-004: Azure for Cloud Hosting

**Decision:** Deploy on Azure with EU-region hosting (West Europe or North Europe).

**Context:** Serving regulated European financial institutions that care about data residency and compliance certifications.

**Rationale:**
- Strong compliance story with European enterprises (ISO 27001, SOC 2, GDPR compliance tools)
- EU data centers with data residency guarantees
- Azure is common in financial services — reduces buyer friction
- Good PostgreSQL managed service (Azure Database for PostgreSQL Flexible Server)
- Container Apps for Docker deployment without Kubernetes overhead

**Alternative considered:** AWS (equally capable, but Azure has stronger brand recognition with European financial institutions). GCP (less enterprise presence in Nordics).

---

## ADR-005: Jinja2 Templates for Document Generation

**Decision:** Use Jinja2 templates combined with python-docx and WeasyPrint for generating recommendation packs and compliance documents.

**Context:** Need to generate structured Word and PDF documents with consistent formatting, variable content, and compliance-required sections.

**Rationale:**
- Jinja2 templates are version-controlled, auditable, and easy to update
- python-docx handles Word output well for most formatting needs
- WeasyPrint converts HTML/CSS to PDF — good for styled PDF output
- Templates can be organization-specific (different branding, different required sections)
- Non-technical compliance team members can review template structure

**Consequences:** Each document type has a Jinja2 template in `backend/app/prompts/templates/`. Template versioning is tracked so we know which template generated which document (stored in Document.template_id).

---

## ADR-006: Structured LLM Outputs via Pydantic

**Decision:** All LLM responses that feed into the system (recommendations, evidence, compliance checks) must be parsed into Pydantic models. No free-text LLM output stored directly.

**Context:** The Reasoner generates recommendations that need to be structured (reasoning chains, assumptions, evidence citations). Storing raw LLM text would make compliance checks, auditing, and display unreliable.

**Rationale:**
- Pydantic validation catches malformed LLM output before it enters the database
- Structured output enables programmatic compliance checks (Control module)
- Evidence citations can be verified against actual KnowledgeItem IDs
- Reasoning chains can be displayed step-by-step in the Workbench UI
- Makes the system more testable and debuggable

**Implementation:** Use Claude's structured output capabilities. Define Pydantic schemas for each output type. Retry with clearer instructions if parsing fails. Log all raw LLM responses for debugging (separate from the parsed output).

---

## ADR-007: Prompt Templates Separated from Code

**Decision:** All LLM prompts live in `backend/app/prompts/` as Jinja2 template files, never hardcoded in Python service files.

**Context:** Prompts will be iterated frequently. Mixing them into business logic makes them hard to find, version, and review.

**Rationale:**
- Prompts can be reviewed and updated without touching application code
- Version control gives full history of prompt changes
- Different organizations might need prompt variants (future)
- Compliance team can audit what instructions the AI receives
- Prompt template version is logged in audit trail

**Consequences:** Service files import and render templates. Prompt template filenames follow a convention: `{module}_{task}_v{version}.jinja2` (e.g., `reasoner_recommendation_v1.jinja2`).

---

## ADR-008: Event-Driven Audit Trail

**Decision:** Use an event-driven pattern for the audit trail. Service functions emit audit events, and a central audit service writes them.

**Context:** Audit entries need to be created consistently across all modules. Scattering audit writes throughout the codebase leads to gaps.

**Rationale:**
- Single place to enforce audit entry structure and completeness
- Services don't need to know about audit implementation details
- Easier to add new audit events without modifying existing services
- Can add async processing later (write to queue, then persist) without changing callers

**Implementation (MVP):** Simple function calls to an `audit_service.log()` method within the same transaction. Not a full event bus — that's premature. Just a clean service interface.

```python
await audit_service.log(
    case_id=case.id,
    action=AuditAction.RECOMMENDATION_GENERATED,
    actor_id=current_user.id,
    actor_type=ActorType.USER,
    details={...}
)
```
