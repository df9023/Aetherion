"""Add regulatory_changes, case_impacts, enums, and audit actions for Regulatory Pulse.

Revision ID: 008
Revises: 007
Create Date: 2026-04-08
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums
    severity = postgresql.ENUM(
        "critical",
        "high",
        "medium",
        "low",
        name="regulatorychangeseverity",
    )
    severity.create(op.get_bind(), checkfirst=True)

    impact_status = postgresql.ENUM(
        "open",
        "acknowledged",
        "resolved",
        "not_applicable",
        name="caseimpactstatus",
    )
    impact_status.create(op.get_bind(), checkfirst=True)

    # Add new audit action values
    op.execute(
        "ALTER TYPE auditaction ADD VALUE IF NOT EXISTS 'regulatory_change_created'"
    )
    op.execute(
        "ALTER TYPE auditaction ADD VALUE IF NOT EXISTS 'impact_scan_completed'"
    )
    op.execute(
        "ALTER TYPE auditaction ADD VALUE IF NOT EXISTS 'impact_resolved'"
    )
    op.execute(
        "ALTER TYPE auditaction ADD VALUE IF NOT EXISTS 'impact_acknowledged'"
    )

    # regulatory_changes table
    op.create_table(
        "regulatory_changes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column("source_url", sa.String(length=1024), nullable=True),
        sa.Column(
            "severity",
            postgresql.ENUM(
                "critical",
                "high",
                "medium",
                "low",
                name="regulatorychangeseverity",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "affected_case_types",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "affected_agreements",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "affected_tags",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("knowledge_item_id", sa.UUID(), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["knowledge_item_id"], ["knowledge_items.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_regulatory_changes_organization_id",
        "regulatory_changes",
        ["organization_id"],
    )
    op.create_index(
        "ix_regulatory_changes_published_at",
        "regulatory_changes",
        ["published_at"],
    )

    # case_impacts table
    op.create_table(
        "case_impacts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("regulatory_change_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("match_reason", sa.Text(), nullable=False),
        sa.Column(
            "affected_sections",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "open",
                "acknowledged",
                "resolved",
                "not_applicable",
                name="caseimpactstatus",
                create_type=False,
            ),
            nullable=False,
            server_default="open",
        ),
        sa.Column("resolved_by", sa.UUID(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(
            ["regulatory_change_id"], ["regulatory_changes.id"]
        ),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"]),
        sa.ForeignKeyConstraint(["resolved_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "regulatory_change_id", "case_id", name="uq_case_impact_change_case"
        ),
    )
    op.create_index(
        "ix_case_impacts_organization_id",
        "case_impacts",
        ["organization_id"],
    )
    op.create_index(
        "ix_case_impacts_regulatory_change_id",
        "case_impacts",
        ["regulatory_change_id"],
    )
    op.create_index("ix_case_impacts_case_id", "case_impacts", ["case_id"])
    op.create_index("ix_case_impacts_status", "case_impacts", ["status"])


def downgrade() -> None:
    op.drop_index("ix_case_impacts_status", table_name="case_impacts")
    op.drop_index("ix_case_impacts_case_id", table_name="case_impacts")
    op.drop_index(
        "ix_case_impacts_regulatory_change_id", table_name="case_impacts"
    )
    op.drop_index("ix_case_impacts_organization_id", table_name="case_impacts")
    op.drop_table("case_impacts")

    op.drop_index(
        "ix_regulatory_changes_published_at", table_name="regulatory_changes"
    )
    op.drop_index(
        "ix_regulatory_changes_organization_id", table_name="regulatory_changes"
    )
    op.drop_table("regulatory_changes")

    op.execute("DROP TYPE IF EXISTS caseimpactstatus")
    op.execute("DROP TYPE IF EXISTS regulatorychangeseverity")
    # Note: new auditaction values cannot be trivially removed
