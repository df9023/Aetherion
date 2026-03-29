"""Add client_organizations table and client_organization_id FK on clients

Revision ID: 005
Revises: 004
Create Date: 2026-03-29
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "client_organizations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("org_number", sa.String(20), nullable=True),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column(
            "collective_agreement",
            postgresql.ENUM(
                "ITP1", "ITP2", "SAF_LO", "KAP_KL", "AKAP_KL", "PA16", "other", "none",
                name="collectiveagreement",
                create_type=False,
            ),
            nullable=True,
        ),
        sa.Column("contact_person", sa.String(255), nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("contact_phone", sa.String(50), nullable=True),
        sa.Column("employee_count", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_client_organizations_organization_id",
        "client_organizations",
        ["organization_id"],
    )

    op.add_column(
        "clients",
        sa.Column("client_organization_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_clients_client_organization_id",
        "clients",
        "client_organizations",
        ["client_organization_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_clients_client_organization_id", "clients", type_="foreignkey")
    op.drop_column("clients", "client_organization_id")
    op.drop_index("ix_client_organizations_organization_id", "client_organizations")
    op.drop_table("client_organizations")
