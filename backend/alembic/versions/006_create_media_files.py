"""create media_files table

Revision ID: 006
Revises: 005
Create Date: 2026-03-22
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "006"
down_revision: str | None = "005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "media_files",
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
            "uploaded_by",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("gcs_path", sa.String(500), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("context_type", sa.String(20), nullable=False),
        sa.Column("context_id", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("idx_media_files_family", "media_files", ["family_id"])
    op.create_index(
        "idx_media_files_context", "media_files", ["context_type", "context_id"]
    )


def downgrade() -> None:
    op.drop_index("idx_media_files_context")
    op.drop_index("idx_media_files_family")
    op.drop_table("media_files")
