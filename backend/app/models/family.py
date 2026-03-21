import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.calendar_event import CalendarEvent
    from app.models.chat_room import ChatRoom
    from app.models.media_file import MediaFile
    from app.models.user import User


class Family(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "families"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    invite_code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    plan: Mapped[str] = mapped_column(String(20), nullable=False, default="free")
    icon_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="family")
    chat_rooms: Mapped[list["ChatRoom"]] = relationship(
        "ChatRoom", back_populates="family"
    )
    calendar_events: Mapped[list["CalendarEvent"]] = relationship(
        "CalendarEvent", back_populates="family"
    )
    media_files: Mapped[list["MediaFile"]] = relationship(
        "MediaFile", back_populates="family"
    )

    def __repr__(self) -> str:
        return f"<Family id={self.id} name={self.name}>"
