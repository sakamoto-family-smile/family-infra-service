"""create calendar_events table

Revision ID: 004
Revises: 003
Create Date: 2026-03-22
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "004"
down_revision: str | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "calendar_events",
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
        sa.Column(
            "created_by",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_at", sa.DateTime(), nullable=False),
        sa.Column("end_at", sa.DateTime(), nullable=False),
        sa.Column(
            "is_all_day", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("location", sa.String(300), nullable=True),
        sa.Column("color", sa.String(7), nullable=True),
        sa.Column("recurrence_rule", sa.String(255), nullable=True),
        sa.Column("reminder_minutes", sa.Integer(), nullable=True),
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
    op.create_index(
        "idx_calendar_events_family", "calendar_events", ["family_id", "start_at"]
    )
    op.create_index(
        "idx_calendar_events_creator", "calendar_events", ["created_by"]
    )


def downgrade() -> None:
    op.drop_index("idx_calendar_events_creator")
    op.drop_index("idx_calendar_events_family")
    op.drop_table("calendar_events")
