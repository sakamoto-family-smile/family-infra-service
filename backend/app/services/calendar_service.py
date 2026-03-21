import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.calendar_event import CalendarEvent
from app.models.calendar_event_attendee import CalendarEventAttendee
from app.repositories.calendar_event_repository import CalendarEventRepository
from app.schemas.calendar_event import CalendarEventCreate, CalendarEventUpdate
from app.services.notification_service import NotificationService


class CalendarService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = CalendarEventRepository(db)
        self.notification_service = NotificationService()

    async def create(
        self,
        family_id: uuid.UUID,
        created_by: uuid.UUID,
        data: CalendarEventCreate,
    ) -> CalendarEvent:
        event = CalendarEvent(
            family_id=family_id,
            created_by=created_by,
            title=data.title,
            description=data.description,
            start_at=data.start_at,
            end_at=data.end_at,
            is_all_day=data.is_all_day,
            location=data.location,
            color=data.color,
            recurrence_rule=data.recurrence_rule,
            reminder_minutes=data.reminder_minutes,
        )
        created = await self.repo.create(event)

        # Add attendees
        for user_id in data.attendee_ids:
            attendee = CalendarEventAttendee(
                event_id=created.id, user_id=user_id
            )
            await self.repo.add_attendee(attendee)

        # Schedule reminder if set
        if data.reminder_minutes is not None:
            await self.notification_service.schedule_reminder(
                event_id=str(created.id),
                start_at=data.start_at,
                reminder_minutes=data.reminder_minutes,
            )

        return await self.repo.get_by_id(created.id)  # type: ignore[return-value]

    async def get(self, event_id: uuid.UUID) -> CalendarEvent:
        event = await self.repo.get_by_id(event_id)
        if not event:
            raise NotFoundException("Calendar event not found")
        return event

    async def list_by_family(
        self,
        family_id: uuid.UUID,
        start: str | None = None,
        end: str | None = None,
    ) -> list[CalendarEvent]:
        from datetime import datetime
        start_dt = datetime.fromisoformat(start) if start else None
        end_dt = datetime.fromisoformat(end) if end else None
        return await self.repo.list_by_family(family_id, start_dt, end_dt)

    async def update(
        self,
        event_id: uuid.UUID,
        family_id: uuid.UUID,
        data: CalendarEventUpdate,
    ) -> CalendarEvent:
        event = await self.get(event_id)
        if str(event.family_id) != str(family_id):
            raise ForbiddenException("Event does not belong to this family")

        for field, value in data.model_dump(exclude_none=True).items():
            setattr(event, field, value)

        return await self.repo.update(event)

    async def delete(self, event_id: uuid.UUID, family_id: uuid.UUID) -> None:
        event = await self.get(event_id)
        if str(event.family_id) != str(family_id):
            raise ForbiddenException("Event does not belong to this family")
        await self.repo.delete(event)
