"""create users table

Revision ID: 002
Revises: 001
Create Date: 2026-03-22
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "family_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("families.id"),
            nullable=False,
        ),
        sa.Column("firebase_uid", sa.String(128), nullable=False, unique=True),
        sa.Column("display_name", sa.String(50), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("role", sa.String(20), nullable=False, server_default="member"),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("idx_users_family_id", "users", ["family_id"])
    op.create_index("idx_users_firebase_uid", "users", ["firebase_uid"])


def downgrade() -> None:
    op.drop_index("idx_users_firebase_uid")
    op.drop_index("idx_users_family_id")
    op.drop_table("users")
