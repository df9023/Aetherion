"""Add reasoning_metadata JSONB column to recommendations.

Revision ID: 006
Revises: 005
Create Date: 2026-03-29
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "recommendations",
        sa.Column("reasoning_metadata", postgresql.JSONB(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("recommendations", "reasoning_metadata")
