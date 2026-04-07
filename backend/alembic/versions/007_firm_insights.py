"""Add firm_insights table, FirmInsightCategory enum, and INSIGHT_CREATED audit action.

Revision ID: 007
Revises: 006
Create Date: 2026-04-07
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create FirmInsightCategory enum
    firm_insight_category = postgresql.ENUM(
        "client_specific",
        "product_tip",
        "process_note",
        "compliance_tip",
        "lesson_learned",
        "general",
        name="firminsightcategory",
    )
    firm_insight_category.create(op.get_bind(), checkfirst=True)

    # Add new audit action enum value (INSIGHT_CREATED)
    op.execute("ALTER TYPE auditaction ADD VALUE IF NOT EXISTS 'insight_created'")

    op.create_table(
        "firm_insights",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "category",
            postgresql.ENUM(
                "client_specific",
                "product_tip",
                "process_note",
                "compliance_tip",
                "lesson_learned",
                "general",
                name="firminsightcategory",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "case_types",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "collective_agreements",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("client_organization_id", sa.UUID(), nullable=True),
        sa.Column(
            "tags",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("source_case_id", sa.UUID(), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
        sa.Column(
            "upvotes", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "upvoted_by",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["client_organization_id"], ["client_organizations.id"]
        ),
        sa.ForeignKeyConstraint(["source_case_id"], ["cases.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_firm_insights_organization_id",
        "firm_insights",
        ["organization_id"],
    )
    op.create_index(
        "ix_firm_insights_client_organization_id",
        "firm_insights",
        ["client_organization_id"],
    )
    op.create_index(
        "ix_firm_insights_source_case_id",
        "firm_insights",
        ["source_case_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_firm_insights_source_case_id", table_name="firm_insights")
    op.drop_index(
        "ix_firm_insights_client_organization_id", table_name="firm_insights"
    )
    op.drop_index("ix_firm_insights_organization_id", table_name="firm_insights")
    op.drop_table("firm_insights")
    op.execute("DROP TYPE IF EXISTS firminsightcategory")
    # Note: enum value 'insight_created' cannot be trivially removed from auditaction
