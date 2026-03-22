"""create calendar_event_attendees table

Revision ID: 005
Revises: 004
Create Date: 2026-03-22
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "005"
down_revision: str | None = "004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "calendar_event_attendees",
        sa.Column(
            "id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "event_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("calendar_events.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "status", sa.String(20), nullable=False, server_default="tentative"
        ),
        sa.Column("responded_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("event_id", "user_id"),
    )


def downgrade() -> None:
    op.drop_table("calendar_event_attendees")
