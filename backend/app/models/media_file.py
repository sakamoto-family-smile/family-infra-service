import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.family import Family
    from app.models.user import User


class MediaFile(Base, UUIDMixin):
    __tablename__ = "media_files"

    family_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("families.id"), nullable=False
    )
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    gcs_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    context_type: Mapped[str] = mapped_column(String(20), nullable=False)
    context_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )

    # Relationships
    family: Mapped["Family"] = relationship("Family", back_populates="media_files")
    uploader: Mapped["User"] = relationship("User", back_populates="media_files")

    __table_args__ = (
        Index("idx_media_files_family", "family_id"),
        Index("idx_media_files_context", "context_type", "context_id"),
    )

    def __repr__(self) -> str:
        return f"<MediaFile id={self.id} file_name={self.file_name}>"
