import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.calendar_event import CalendarEvent
from app.models.calendar_event_attendee import CalendarEventAttendee


class CalendarEventRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, event_id: uuid.UUID) -> CalendarEvent | None:
        result = await self.db.execute(
            select(CalendarEvent)
            .options(selectinload(CalendarEvent.attendees))
            .where(CalendarEvent.id == event_id)
        )
        return result.scalar_one_or_none()

    async def list_by_family(
        self,
        family_id: uuid.UUID,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[CalendarEvent]:
        query = (
            select(CalendarEvent)
            .options(selectinload(CalendarEvent.attendees))
            .where(CalendarEvent.family_id == family_id)
            .order_by(CalendarEvent.start_at)
        )
        if start:
            query = query.where(CalendarEvent.start_at >= start)
        if end:
            query = query.where(CalendarEvent.end_at <= end)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, event: CalendarEvent) -> CalendarEvent:
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event, ["attendees"])
        return event

    async def update(self, event: CalendarEvent) -> CalendarEvent:
        await self.db.flush()
        await self.db.refresh(event, ["attendees"])
        return event

    async def delete(self, event: CalendarEvent) -> None:
        await self.db.delete(event)
        await self.db.flush()

    async def add_attendee(self, attendee: CalendarEventAttendee) -> CalendarEventAttendee:
        self.db.add(attendee)
        await self.db.flush()
        await self.db.refresh(attendee)
        return attendee

    async def remove_attendee(
        self, event_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        result = await self.db.execute(
            select(CalendarEventAttendee).where(
                CalendarEventAttendee.event_id == event_id,
                CalendarEventAttendee.user_id == user_id,
            )
        )
        attendee = result.scalar_one_or_none()
        if attendee:
            await self.db.delete(attendee)
            await self.db.flush()
