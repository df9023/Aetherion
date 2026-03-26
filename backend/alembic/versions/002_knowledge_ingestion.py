"""Knowledge ingestion: flexible embedding dim, nullable audit case_id, knowledge_ingested action

Revision ID: 002
Revises: 001
Create Date: 2026-03-26
"""

from alembic import op

revision = "002"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove fixed dimension constraint on embedding column
    # This allows both 1024 (Voyage) and 1536 (OpenAI) dimension vectors
    op.execute(
        "ALTER TABLE knowledge_items ALTER COLUMN embedding TYPE vector USING embedding::vector"
    )

    # Make audit_entries.case_id nullable (knowledge ingestion has no case)
    op.alter_column("audit_entries", "case_id", nullable=True)

    # Add KNOWLEDGE_INGESTED to audit_action enum
    op.execute("ALTER TYPE auditaction ADD VALUE IF NOT EXISTS 'knowledge_ingested'")


def downgrade() -> None:
    op.alter_column("audit_entries", "case_id", nullable=False)
    op.execute(
        "ALTER TABLE knowledge_items ALTER COLUMN embedding TYPE vector(1536) USING embedding::vector(1536)"
    )
