import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.calendar_event import CalendarEvent
    from app.models.user import User


class CalendarEventAttendee(Base, UUIDMixin):
    __tablename__ = "calendar_event_attendees"

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("calendar_events.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="tentative"
    )
    responded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False), nullable=True
    )

    # Relationships
    event: Mapped["CalendarEvent"] = relationship(
        "CalendarEvent", back_populates="attendees"
    )
    user: Mapped["User"] = relationship("User", back_populates="event_attendances")

    __table_args__ = (UniqueConstraint("event_id", "user_id"),)

    def __repr__(self) -> str:
        return f"<CalendarEventAttendee event_id={self.event_id} user_id={self.user_id}>"
