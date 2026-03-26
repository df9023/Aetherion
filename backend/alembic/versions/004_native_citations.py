"""Native citations: cited_text, document_index, char indices, knowledge_item_id on evidences

Revision ID: 004
Revises: 003
Create Date: 2026-03-26
"""

import sqlalchemy as sa
from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "evidences",
        sa.Column("cited_text", sa.Text(), nullable=True),
    )
    op.add_column(
        "evidences",
        sa.Column("document_index", sa.Integer(), nullable=True),
    )
    op.add_column(
        "evidences",
        sa.Column("start_char_index", sa.Integer(), nullable=True),
    )
    op.add_column(
        "evidences",
        sa.Column("end_char_index", sa.Integer(), nullable=True),
    )
    op.add_column(
        "evidences",
        sa.Column(
            "knowledge_item_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("knowledge_items.id"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("evidences", "knowledge_item_id")
    op.drop_column("evidences", "end_char_index")
    op.drop_column("evidences", "start_char_index")
    op.drop_column("evidences", "document_index")
    op.drop_column("evidences", "cited_text")
