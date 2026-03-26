"""Citation validation: evidence verified/status, knowledge source_location

Revision ID: 003
Revises: 002
Create Date: 2026-03-26
"""

import sqlalchemy as sa
from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add citation verification fields to evidences
    op.add_column(
        "evidences",
        sa.Column("verified", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.add_column(
        "evidences",
        sa.Column(
            "verification_status",
            sa.String(30),
            nullable=False,
            server_default="verified",
        ),
    )

    # Add source_location to knowledge_items for document position tracing
    op.add_column(
        "knowledge_items",
        sa.Column("source_location", sa.dialects.postgresql.JSONB(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("knowledge_items", "source_location")
    op.drop_column("evidences", "verification_status")
    op.drop_column("evidences", "verified")
