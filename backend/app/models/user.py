import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.calendar_event import CalendarEvent
    from app.models.calendar_event_attendee import CalendarEventAttendee
    from app.models.chat_room import ChatRoom
    from app.models.family import Family
    from app.models.media_file import MediaFile


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    family_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("families.id"), nullable=False
    )
    firebase_uid: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="member")
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False), nullable=True
    )

    # Relationships
    family: Mapped["Family"] = relationship("Family", back_populates="users")
    created_chat_rooms: Mapped[list["ChatRoom"]] = relationship(
        "ChatRoom", back_populates="creator"
    )
    calendar_events: Mapped[list["CalendarEvent"]] = relationship(
        "CalendarEvent", back_populates="creator"
    )
    event_attendances: Mapped[list["CalendarEventAttendee"]] = relationship(
        "CalendarEventAttendee", back_populates="user"
    )
    media_files: Mapped[list["MediaFile"]] = relationship(
        "MediaFile", back_populates="uploader"
    )

    __table_args__ = (
        Index("idx_users_family_id", "family_id"),
        Index("idx_users_firebase_uid", "firebase_uid"),
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
