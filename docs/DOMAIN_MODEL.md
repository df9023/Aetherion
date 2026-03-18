# Aetherion Domain Model

This document defines the core data entities for Aetherion. All database schemas, API contracts, and service interfaces should align with these models.

## Core Entities

### Client
The end client whose pension situation is being analyzed.

```
Client
├── id: UUID
├── organization_id: FK → Organization
├── external_id: string (optional — ID from source system)
├── name: string (encrypted at rest)
├── date_of_birth: date
├── employment_status: enum (employed, self_employed, retired, other)
├── employer_name: string (optional)
├── collective_agreement: enum (ITP1, ITP2, SAF_LO, KAP_KL, AKAP_KL, PA16, other, none)
├── annual_income: decimal (optional, encrypted)
├── desired_retirement_age: integer (optional)
├── risk_profile: enum (low, moderate, high) (optional)
├── created_at: timestamp
├── updated_at: timestamp
└── created_by: FK → User
```

### Case
A pension advisory case — the central work unit in Aetherion. One client can have multiple cases over time.

```
Case
├── id: UUID
├── client_id: FK → Client
├── assigned_to: FK → User
├── case_type: enum (pension_review, transfer_advice, salary_exchange, retirement_planning, survivor_protection, decumulation, other)
├── status: enum (draft, in_preparation, ready_for_review, in_review, approved, completed, archived)
├── title: string
├── summary: text (optional)
├── meeting_date: timestamp (optional)
├── created_at: timestamp
├── updated_at: timestamp
├── completed_at: timestamp (optional)
└── organization_id: FK → Organization
```

### Recommendation
The structured output of the Reasoner — an evidence-backed recommendation for a case.

```
Recommendation
├── id: UUID
├── case_id: FK → Case
├── version: integer (increments on each revision)
├── recommendation_type: enum (product_selection, allocation_change, transfer, salary_exchange, withdrawal_plan, coverage_change, other)
├── summary: text
├── reasoning_chain: JSONB (structured reasoning steps)
├── assumptions: JSONB (list of assumptions made)
├── scenarios: JSONB (optional — comparison scenarios generated)
├── suitability_score: decimal (optional — internal quality metric)
├── status: enum (draft, pending_review, approved, rejected, superseded)
├── created_at: timestamp
├── created_by: FK → User (or system)
└── approved_by: FK → User (optional)
```

### Evidence
Supporting sources linked to a recommendation. Powers the Reasoner's explainability.

```
Evidence
├── id: UUID
├── recommendation_id: FK → Recommendation
├── source_type: enum (product_rule, regulation, internal_policy, market_data, client_data, precedent, expert_knowledge)
├── source_reference: string (document name, section, URL, or knowledge_item_id)
├── content_snippet: text (relevant excerpt)
├── relevance_explanation: text (why this evidence supports the recommendation)
├── confidence: decimal (0.0 to 1.0)
└── created_at: timestamp
```

### AuditEntry
Immutable compliance trail. Every significant action on a case creates an audit entry.

```
AuditEntry
├── id: UUID
├── case_id: FK → Case
├── action: enum (case_created, case_assigned, recommendation_generated, recommendation_edited, recommendation_reviewed, recommendation_approved, recommendation_rejected, document_generated, compliance_check_passed, compliance_check_failed, case_completed, knowledge_referenced, workflow_step_completed)
├── actor_id: FK → User (or system identifier)
├── actor_type: enum (user, system)
├── details: JSONB (action-specific metadata)
├── timestamp: timestamp
└── ip_address: string (optional)
```

### KnowledgeItem
A unit of institutional knowledge in the Memory module.

```
KnowledgeItem
├── id: UUID
├── organization_id: FK → Organization
├── title: string
├── content: text
├── category: enum (product_rule, internal_policy, regulatory_requirement, playbook, precedent, faq, process_guide)
├── source: string (where this knowledge came from)
├── tags: string[] (for filtering)
├── embedding: vector(1536) (pgvector — for semantic search)
├── is_active: boolean
├── effective_date: date (optional — when this rule/policy takes effect)
├── expiry_date: date (optional — when this rule/policy expires)
├── created_at: timestamp
├── updated_at: timestamp
├── created_by: FK → User
└── approved_by: FK → User (optional)
```

### Document
A generated document (recommendation pack, compliance report, client explanation).

```
Document
├── id: UUID
├── case_id: FK → Case
├── recommendation_id: FK → Recommendation (optional)
├── document_type: enum (recommendation_pack, suitability_assessment, needs_analysis, client_explanation, meeting_notes, compliance_report)
├── title: string
├── template_id: string (optional — which Jinja2 template was used)
├── file_path: string (storage location)
├── file_format: enum (docx, pdf)
├── generated_at: timestamp
├── generated_by: FK → User (or system)
└── version: integer
```

### Workflow
A Flow orchestration instance tracking a case through its lifecycle.

```
Workflow
├── id: UUID
├── case_id: FK → Case
├── workflow_template: string (which workflow definition is being followed)
├── current_step: string
├── status: enum (active, paused, completed, failed, cancelled)
├── steps_completed: JSONB (list of completed steps with timestamps)
├── pending_actions: JSONB (list of actions waiting for input)
├── created_at: timestamp
├── updated_at: timestamp
└── completed_at: timestamp (optional)
```

### Organization
The institutional customer (pension company, advisory firm, insurer).

```
Organization
├── id: UUID
├── name: string
├── org_type: enum (pension_provider, advisory_firm, life_insurer, benefits_consultant, other)
├── jurisdiction: string (e.g., "SE" for Sweden)
├── settings: JSONB (org-specific configuration)
├── created_at: timestamp
└── is_active: boolean
```

### User
An individual user within an organization.

```
User
├── id: UUID
├── organization_id: FK → Organization
├── email: string
├── name: string
├── role: enum (advisor, specialist, compliance_reviewer, admin, readonly)
├── workos_user_id: string (external auth reference)
├── created_at: timestamp
├── last_active_at: timestamp
└── is_active: boolean
```

## Key Relationships

```
Organization ──< User
Organization ──< Client
Organization ──< KnowledgeItem
User ──< Case (assigned_to)
Client ──< Case
Case ──< Recommendation
Case ──< AuditEntry
Case ──< Document
Case ──< Workflow
Recommendation ──< Evidence
Recommendation ──< Document
```

## Design Principles

1. **Immutability for compliance**: AuditEntry is append-only. Recommendations are versioned, not edited in place.
2. **Soft deletes**: Use is_active flags, never hard delete case data.
3. **Encryption**: Client PII fields encrypted at rest. Use application-level encryption, not just database-level.
4. **Multi-tenancy**: Organization-scoped queries everywhere. Never leak data across organizations.
5. **Audit everything**: Every state change on a Case or Recommendation creates an AuditEntry.
6. **Structured LLM outputs**: reasoning_chain, assumptions, and scenarios in Recommendation are structured JSONB, not free text. This powers the Reasoner's explainability.
