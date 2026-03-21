import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.family import Family
    from app.models.user import User


class ChatRoom(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chat_rooms"

    family_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("families.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    last_message_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False), nullable=True
    )

    # Relationships
    family: Mapped["Family"] = relationship("Family", back_populates="chat_rooms")
    creator: Mapped["User"] = relationship("User", back_populates="created_chat_rooms")

    __table_args__ = (
        Index("idx_chat_rooms_family", "family_id"),
        Index("idx_chat_rooms_sort", "family_id", "last_message_at"),
    )

    def __repr__(self) -> str:
        return f"<ChatRoom id={self.id} name={self.name}>"
