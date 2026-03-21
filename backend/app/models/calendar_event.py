import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.calendar_event_attendee import CalendarEventAttendee
    from app.models.family import Family
    from app.models.user import User


class CalendarEvent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "calendar_events"

    family_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("families.id"), nullable=False
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    is_all_day: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    location: Mapped[str | None] = mapped_column(String(300), nullable=True)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    recurrence_rule: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reminder_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    family: Mapped["Family"] = relationship("Family", back_populates="calendar_events")
    creator: Mapped["User"] = relationship("User", back_populates="calendar_events")
    attendees: Mapped[list["CalendarEventAttendee"]] = relationship(
        "CalendarEventAttendee", back_populates="event", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_calendar_events_family", "family_id", "start_at"),
        Index("idx_calendar_events_creator", "created_by"),
    )

    def __repr__(self) -> str:
        return f"<CalendarEvent id={self.id} title={self.title}>"
