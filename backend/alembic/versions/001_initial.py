"""Initial migration

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Organizations
    op.create_table(
        "organizations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "org_type",
            sa.Enum(
                "pension_provider",
                "advisory_firm",
                "life_insurer",
                "benefits_consultant",
                "other",
                name="organizationtype",
            ),
            nullable=False,
        ),
        sa.Column("jurisdiction", sa.String(length=10), nullable=False),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "advisor",
                "specialist",
                "compliance_reviewer",
                "admin",
                "readonly",
                name="userrole",
            ),
            nullable=False,
        ),
        sa.Column("workos_user_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    # Clients
    op.create_table(
        "clients",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("external_id", sa.String(length=512), nullable=True),
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column(
            "employment_status",
            sa.Enum("employed", "self_employed", "retired", "other", name="employmentstatus"),
            nullable=False,
        ),
        sa.Column("employer_name", sa.String(length=255), nullable=True),
        sa.Column(
            "collective_agreement",
            sa.Enum(
                "ITP1",
                "ITP2",
                "SAF_LO",
                "KAP_KL",
                "AKAP_KL",
                "PA16",
                "other",
                "none",
                name="collectiveagreement",
            ),
            nullable=False,
        ),
        sa.Column("annual_income", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("desired_retirement_age", sa.Integer(), nullable=True),
        sa.Column(
            "risk_profile",
            sa.Enum("low", "moderate", "high", name="riskprofile"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Cases
    op.create_table(
        "cases",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("client_id", sa.UUID(), nullable=False),
        sa.Column("assigned_to", sa.UUID(), nullable=False),
        sa.Column(
            "case_type",
            sa.Enum(
                "pension_review",
                "transfer_advice",
                "salary_exchange",
                "retirement_planning",
                "survivor_protection",
                "decumulation",
                "other",
                name="casetype",
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "draft",
                "in_preparation",
                "ready_for_review",
                "in_review",
                "approved",
                "completed",
                "archived",
                name="casestatus",
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("meeting_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["assigned_to"], ["users.id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Recommendations
    op.create_table(
        "recommendations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column(
            "recommendation_type",
            sa.Enum(
                "product_selection",
                "allocation_change",
                "transfer",
                "salary_exchange",
                "withdrawal_plan",
                "coverage_change",
                "other",
                name="recommendationtype",
            ),
            nullable=False,
        ),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("reasoning_chain", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("assumptions", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("scenarios", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("suitability_score", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "draft",
                "pending_review",
                "approved",
                "rejected",
                "superseded",
                name="recommendationstatus",
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("approved_by", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Evidences
    op.create_table(
        "evidences",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("recommendation_id", sa.UUID(), nullable=False),
        sa.Column(
            "source_type",
            sa.Enum(
                "product_rule",
                "regulation",
                "internal_policy",
                "market_data",
                "client_data",
                "precedent",
                "expert_knowledge",
                name="evidencesourcetype",
            ),
            nullable=False,
        ),
        sa.Column("source_reference", sa.String(length=1024), nullable=False),
        sa.Column("content_snippet", sa.Text(), nullable=False),
        sa.Column("relevance_explanation", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["recommendation_id"], ["recommendations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Audit Entries
    op.create_table(
        "audit_entries",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column(
            "action",
            sa.Enum(
                "case_created",
                "case_assigned",
                "recommendation_generated",
                "recommendation_edited",
                "recommendation_reviewed",
                "recommendation_approved",
                "recommendation_rejected",
                "document_generated",
                "compliance_check_passed",
                "compliance_check_failed",
                "case_completed",
                "knowledge_referenced",
                "workflow_step_completed",
                "workflow_paused",
                "workflow_resumed",
                name="auditaction",
            ),
            nullable=False,
        ),
        sa.Column("actor_id", sa.UUID(), nullable=False),
        sa.Column(
            "actor_type",
            sa.Enum("user", "system", name="actortype"),
            nullable=False,
        ),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_entries_case_id", "audit_entries", ["case_id"])
    op.create_index("ix_audit_entries_timestamp", "audit_entries", ["timestamp"])

    # Knowledge Items
    op.create_table(
        "knowledge_items",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "category",
            sa.Enum(
                "product_rule",
                "internal_policy",
                "regulatory_requirement",
                "playbook",
                "precedent",
                "faq",
                "process_guide",
                name="knowledgecategory",
            ),
            nullable=False,
        ),
        sa.Column("source", sa.String(length=512), nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("approved_by", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_knowledge_items_organization_id", "knowledge_items", ["organization_id"])

    # Documents
    op.create_table(
        "documents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("recommendation_id", sa.UUID(), nullable=True),
        sa.Column(
            "document_type",
            sa.Enum(
                "recommendation_pack",
                "suitability_assessment",
                "needs_analysis",
                "client_explanation",
                "meeting_notes",
                "compliance_report",
                name="documenttype",
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("template_id", sa.String(length=255), nullable=True),
        sa.Column("file_path", sa.String(length=1024), nullable=False),
        sa.Column(
            "file_format",
            sa.Enum("docx", "pdf", name="fileformat"),
            nullable=False,
        ),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("generated_by", sa.UUID(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.ForeignKeyConstraint(["generated_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["recommendation_id"], ["recommendations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Workflows
    op.create_table(
        "workflows",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("workflow_template", sa.String(length=255), nullable=False),
        sa.Column("current_step", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            sa.Enum("active", "paused", "completed", "failed", "cancelled", name="workflowstatus"),
            nullable=False,
        ),
        sa.Column("steps_completed", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("pending_actions", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_workflows_case_id", "workflows", ["case_id"])


def downgrade() -> None:
    op.drop_table("workflows")
    op.drop_table("documents")
    op.drop_table("knowledge_items")
    op.drop_table("audit_entries")
    op.drop_table("evidences")
    op.drop_table("recommendations")
    op.drop_table("cases")
    op.drop_table("clients")
    op.drop_table("users")
    op.drop_table("organizations")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS workflowstatus")
    op.execute("DROP TYPE IF EXISTS fileformat")
    op.execute("DROP TYPE IF EXISTS documenttype")
    op.execute("DROP TYPE IF EXISTS knowledgecategory")
    op.execute("DROP TYPE IF EXISTS actortype")
    op.execute("DROP TYPE IF EXISTS auditaction")
    op.execute("DROP TYPE IF EXISTS evidencesourcetype")
    op.execute("DROP TYPE IF EXISTS recommendationstatus")
    op.execute("DROP TYPE IF EXISTS recommendationtype")
    op.execute("DROP TYPE IF EXISTS casestatus")
    op.execute("DROP TYPE IF EXISTS casetype")
    op.execute("DROP TYPE IF EXISTS riskprofile")
    op.execute("DROP TYPE IF EXISTS collectiveagreement")
    op.execute("DROP TYPE IF EXISTS employmentstatus")
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS organizationtype")
