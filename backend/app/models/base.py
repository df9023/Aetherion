import enum

from sqlalchemy import Enum as _SAEnum


def ValueEnum(enum_class):
    """Create a SQLAlchemy Enum that uses the Python enum .value (lowercase)
    instead of .name (UPPERCASE) for PostgreSQL storage."""
    return _SAEnum(
        enum_class,
        values_callable=lambda e: [member.value for member in e],
    )


class EmploymentStatus(str, enum.Enum):
    EMPLOYED = "employed"
    SELF_EMPLOYED = "self_employed"
    RETIRED = "retired"
    OTHER = "other"


class CollectiveAgreement(str, enum.Enum):
    ITP1 = "ITP1"
    ITP2 = "ITP2"
    SAF_LO = "SAF_LO"
    KAP_KL = "KAP_KL"
    AKAP_KL = "AKAP_KL"
    PA16 = "PA16"
    OTHER = "other"
    NONE = "none"


class RiskProfile(str, enum.Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class CaseType(str, enum.Enum):
    PENSION_REVIEW = "pension_review"
    TRANSFER_ADVICE = "transfer_advice"
    SALARY_EXCHANGE = "salary_exchange"
    RETIREMENT_PLANNING = "retirement_planning"
    SURVIVOR_PROTECTION = "survivor_protection"
    DECUMULATION = "decumulation"
    OTHER = "other"


class CaseStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PREPARATION = "in_preparation"
    READY_FOR_REVIEW = "ready_for_review"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class RecommendationType(str, enum.Enum):
    PRODUCT_SELECTION = "product_selection"
    ALLOCATION_CHANGE = "allocation_change"
    TRANSFER = "transfer"
    SALARY_EXCHANGE = "salary_exchange"
    WITHDRAWAL_PLAN = "withdrawal_plan"
    COVERAGE_CHANGE = "coverage_change"
    OTHER = "other"


class RecommendationStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class EvidenceSourceType(str, enum.Enum):
    PRODUCT_RULE = "product_rule"
    REGULATION = "regulation"
    INTERNAL_POLICY = "internal_policy"
    MARKET_DATA = "market_data"
    CLIENT_DATA = "client_data"
    PRECEDENT = "precedent"
    EXPERT_KNOWLEDGE = "expert_knowledge"


class AuditAction(str, enum.Enum):
    CASE_CREATED = "case_created"
    CASE_ASSIGNED = "case_assigned"
    RECOMMENDATION_GENERATED = "recommendation_generated"
    RECOMMENDATION_EDITED = "recommendation_edited"
    REASONING_ANNOTATED = "reasoning_annotated"
    REASONING_REVIEWED = "reasoning_reviewed"
    RECOMMENDATION_REVIEWED = "recommendation_reviewed"
    RECOMMENDATION_APPROVED = "recommendation_approved"
    RECOMMENDATION_REJECTED = "recommendation_rejected"
    DOCUMENT_GENERATED = "document_generated"
    COMPLIANCE_CHECK_PASSED = "compliance_check_passed"
    COMPLIANCE_CHECK_FAILED = "compliance_check_failed"
    CASE_COMPLETED = "case_completed"
    KNOWLEDGE_REFERENCED = "knowledge_referenced"
    WORKFLOW_STEP_COMPLETED = "workflow_step_completed"
    WORKFLOW_PAUSED = "workflow_paused"
    WORKFLOW_RESUMED = "workflow_resumed"
    MEETING_BRIEF_GENERATED = "meeting_brief_generated"
    DOCUMENT_INGESTED = "document_ingested"
    CLIENT_DATA_APPLIED = "client_data_applied"
    KNOWLEDGE_INGESTED = "knowledge_ingested"
    INSIGHT_CREATED = "insight_created"
    REGULATORY_CHANGE_CREATED = "regulatory_change_created"
    IMPACT_SCAN_COMPLETED = "impact_scan_completed"
    IMPACT_RESOLVED = "impact_resolved"
    IMPACT_ACKNOWLEDGED = "impact_acknowledged"


class ActorType(str, enum.Enum):
    USER = "user"
    SYSTEM = "system"


class RegulatoryChangeSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CaseImpactStatus(str, enum.Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    NOT_APPLICABLE = "not_applicable"


class FirmInsightCategory(str, enum.Enum):
    CLIENT_SPECIFIC = "client_specific"
    PRODUCT_TIP = "product_tip"
    PROCESS_NOTE = "process_note"
    COMPLIANCE_TIP = "compliance_tip"
    LESSON_LEARNED = "lesson_learned"
    GENERAL = "general"


class KnowledgeCategory(str, enum.Enum):
    PRODUCT_RULE = "product_rule"
    INTERNAL_POLICY = "internal_policy"
    REGULATORY_REQUIREMENT = "regulatory_requirement"
    PLAYBOOK = "playbook"
    PRECEDENT = "precedent"
    FAQ = "faq"
    PROCESS_GUIDE = "process_guide"


class DocumentType(str, enum.Enum):
    RECOMMENDATION_PACK = "recommendation_pack"
    SUITABILITY_ASSESSMENT = "suitability_assessment"
    NEEDS_ANALYSIS = "needs_analysis"
    CLIENT_EXPLANATION = "client_explanation"
    MEETING_NOTES = "meeting_notes"
    COMPLIANCE_REPORT = "compliance_report"


class FileFormat(str, enum.Enum):
    DOCX = "docx"
    PDF = "pdf"


class WorkflowStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OrganizationType(str, enum.Enum):
    PENSION_PROVIDER = "pension_provider"
    ADVISORY_FIRM = "advisory_firm"
    LIFE_INSURER = "life_insurer"
    BENEFITS_CONSULTANT = "benefits_consultant"
    OTHER = "other"


class UserRole(str, enum.Enum):
    ADVISOR = "advisor"
    SPECIALIST = "specialist"
    COMPLIANCE_REVIEWER = "compliance_reviewer"
    ADMIN = "admin"
    READONLY = "readonly"
