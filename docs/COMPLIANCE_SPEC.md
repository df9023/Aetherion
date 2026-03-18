# Compliance Output Specification — Control Module

This document defines what compliant outputs look like in Aetherion. Claude Code should reference this when building the Control module, document generation, and audit trail functionality.

## What Control Does

Control is the compliance and governance layer. It ensures every recommendation is:
- Auditable (full trail of who did what, when, and why)
- Reviewable (structured for compliance team review)
- Approval-ready (contains all required documentation elements)
- Consistent (same quality bar regardless of which advisor prepared the case)

## Recommendation Pack Structure

A "recommendation pack" is the primary output of a completed case. It's a generated document (Word/PDF) that contains everything needed for compliance review and client communication.

### Required Sections

#### 1. Client Summary (Kundsammanfattning)
- Client name, date of birth, employment status
- Employer and collective agreement (if applicable)
- Current income (relevant for pension calculations)
- Stated retirement goals and desired retirement age
- Risk profile assessment result

#### 2. Needs Analysis (Behovsanalys)
- Client's current pension situation across all three pillars
- Identified gaps or risks (coverage gaps, insufficient savings, concentration risk)
- Client's expressed needs and priorities
- Life situation factors (family, health considerations, other financial obligations)

#### 3. Market/Product Analysis
- Products or solutions considered
- Comparison of relevant alternatives (fees, coverage, flexibility)
- Why certain products were included or excluded

#### 4. Recommendation (Rekommendation)
- Clear statement of what is recommended
- Specific products, allocations, or actions
- Expected outcomes under different scenarios (if applicable)
- Timeline for implementation

#### 5. Reasoning and Evidence (Motivering)
- Why this recommendation is suitable for this specific client
- How the recommendation addresses the identified needs
- Evidence sources cited (product rules, regulations, internal policies)
- Assumptions made and their basis
- Risks and limitations of the recommendation

#### 6. Suitability Assessment (Lämplighetsbedömning)
- Confirmation that the recommendation matches the client's:
  - Knowledge and experience
  - Financial situation
  - Investment objectives and risk tolerance
  - Specific needs and priorities
- Explanation of how suitability was determined

#### 7. Cost Disclosure (Kostnadsinformation)
- All fees and costs associated with the recommendation
- Comparison of costs between alternatives considered
- Impact of costs on expected returns over time

#### 8. Conflict of Interest Disclosure (Intressekonflikter)
- Any conflicts of interest relevant to the recommendation
- How conflicts are managed

#### 9. Advisor Information
- Advisor name and credentials
- Date of advice
- Method of communication (meeting, phone, digital)

### Document Metadata (Not Visible in Document, Stored in System)
- Case ID
- Recommendation version
- All evidence IDs cited
- All knowledge items referenced
- Generation timestamp
- Advisor user ID
- Compliance review status

## Audit Trail Requirements

### What Gets Logged (AuditEntry Records)

Every one of these actions creates an immutable AuditEntry:

| Action | What to Log |
|---|---|
| case_created | Case type, assigned advisor, client reference |
| case_assigned | Previous assignee (if reassigned), new assignee |
| recommendation_generated | Recommendation version, LLM model used, prompt template version, knowledge items retrieved |
| recommendation_edited | Which fields changed, previous values (diff) |
| recommendation_reviewed | Reviewer ID, review outcome (approved/rejected), review comments |
| recommendation_approved | Approver ID, any conditions attached |
| recommendation_rejected | Rejector ID, reason for rejection, required changes |
| document_generated | Document type, template used, recommendation version used |
| compliance_check_passed | Which checks passed, check definitions used |
| compliance_check_failed | Which checks failed, failure reasons, severity |
| case_completed | Final status, total elapsed time |
| knowledge_referenced | Which knowledge items were cited, in which context |
| workflow_step_completed | Step name, duration, outcome |

### Audit Entry Structure

```json
{
  "id": "uuid",
  "case_id": "uuid",
  "action": "recommendation_generated",
  "actor_id": "uuid",
  "actor_type": "system",
  "timestamp": "2025-01-15T14:30:00Z",
  "details": {
    "recommendation_id": "uuid",
    "recommendation_version": 1,
    "llm_model": "claude-sonnet-4-20250514",
    "prompt_template": "recommendation_v2",
    "knowledge_items_retrieved": ["uuid1", "uuid2", "uuid3"],
    "retrieval_query": "ITP1 allocation recommendation for client aged 45",
    "generation_time_ms": 3200
  }
}
```

### Retention
- Audit entries are never deleted
- Minimum retention: 10 years (aligned with Swedish financial regulation retention requirements)
- Entries are append-only — no updates or modifications

## Compliance Checks

The Control module runs automated checks before a recommendation can be marked as "ready for review."

### MVP Checks

1. **Completeness check**: All required sections of the recommendation pack are populated
2. **Suitability alignment**: The recommendation type aligns with the client's stated risk profile and needs
3. **Evidence coverage**: At least one evidence source is cited for the main recommendation
4. **Cost disclosure present**: Fee information is included
5. **Conflict disclosure present**: Conflict of interest section is populated

### Future Checks (Post-MVP)
- Regulatory rule validation (e.g., checking recommendation against FI guidelines)
- Cross-case consistency (flagging if similar clients received very different recommendations)
- Knowledge freshness (warning if cited knowledge items are outdated)
- Concentration risk detection
- Missing coverage gap detection

### Check Output Format

```json
{
  "case_id": "uuid",
  "recommendation_id": "uuid",
  "checked_at": "2025-01-15T14:35:00Z",
  "overall_status": "pass | fail | warning",
  "checks": [
    {
      "check_id": "completeness",
      "status": "pass",
      "message": null
    },
    {
      "check_id": "evidence_coverage",
      "status": "warning",
      "message": "Only 1 evidence source cited. Consider adding supporting sources."
    }
  ]
}
```

## Review Workflow

1. Advisor completes case preparation in Workbench
2. Reasoner generates recommendation
3. Control runs automated compliance checks
4. If checks pass → case status moves to "ready_for_review"
5. If checks fail → advisor is shown what needs fixing
6. Compliance reviewer opens case, reviews recommendation pack
7. Reviewer approves, rejects (with comments), or requests changes
8. On approval → document is finalized, case status moves to "approved"
9. AuditEntry records every step
