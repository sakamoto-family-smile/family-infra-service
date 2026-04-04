import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import ForbiddenException, NotFoundException
from app.schemas.calendar_event import CalendarEventCreate, CalendarEventUpdate
from app.services.calendar_service import CalendarService
from tests.factories.calendar_event_factory import make_calendar_event


@pytest.mark.asyncio
async def test_create_event():
    db = MagicMock()
    family_id = uuid.uuid4()
    created_by = uuid.uuid4()
    event = make_calendar_event(family_id=family_id, created_by=created_by, title="Sports Day")

    with patch.object(CalendarService, "__init__", lambda self, db: None):
        service = CalendarService.__new__(CalendarService)
        service.db = db
        service.repo = MagicMock()
        service.notification_service = MagicMock()

    service.repo.create = AsyncMock(return_value=event)
    service.repo.add_attendee = AsyncMock()
    service.repo.get_by_id = AsyncMock(return_value=event)
    service.notification_service.schedule_reminder = AsyncMock()

    data = CalendarEventCreate(
        title="Sports Day",
        start_at=datetime(2024, 6, 1, 10, 0, tzinfo=timezone.utc),
        end_at=datetime(2024, 6, 1, 11, 0, tzinfo=timezone.utc),
        attendee_ids=[],
    )
    result = await service.create(family_id, created_by, data)
    assert result.title == "Sports Day"


@pytest.mark.asyncio
async def test_get_event_not_found():
    db = MagicMock()
    with patch("app.services.calendar_service.NotificationService"):
        service = CalendarService(db)

    service.repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException):
        await service.get(uuid.uuid4())


@pytest.mark.asyncio
async def test_get_event_success():
    db = MagicMock()
    with patch("app.services.calendar_service.NotificationService"):
        service = CalendarService(db)

    event = make_calendar_event(title="Birthday Party")
    service.repo.get_by_id = AsyncMock(return_value=event)

    result = await service.get(event.id)
    assert result.title == "Birthday Party"


@pytest.mark.asyncio
async def test_list_by_family():
    db = MagicMock()
    with patch("app.services.calendar_service.NotificationService"):
        service = CalendarService(db)

    family_id = uuid.uuid4()
    events = [make_calendar_event(family_id=family_id), make_calendar_event(family_id=family_id)]
    service.repo.list_by_family = AsyncMock(return_value=events)

    result = await service.list_by_family(family_id)
    assert len(result) == 2


@pytest.mark.asyncio
async def test_update_event_success():
    db = MagicMock()
    with patch("app.services.calendar_service.NotificationService"):
        service = CalendarService(db)

    family_id = uuid.uuid4()
    event = make_calendar_event(family_id=family_id, title="Old Title")
    service.repo.get_by_id = AsyncMock(return_value=event)
    service.repo.update = AsyncMock(return_value=event)

    result = await service.update(event.id, family_id, CalendarEventUpdate(title="New Title"))
    assert result.title == "New Title"


@pytest.mark.asyncio
async def test_update_event_wrong_family():
    db = MagicMock()
    with patch("app.services.calendar_service.NotificationService"):
        service = CalendarService(db)

    event = make_calendar_event(family_id=uuid.uuid4())
    service.repo.get_by_id = AsyncMock(return_value=event)

    with pytest.raises(ForbiddenException):
        await service.update(event.id, uuid.uuid4(), CalendarEventUpdate(title="Hack"))


@pytest.mark.asyncio
async def test_delete_event_wrong_family():
    db = MagicMock()
    with patch("app.services.calendar_service.NotificationService"):
        service = CalendarService(db)

    event = make_calendar_event(family_id=uuid.uuid4())
    service.repo.get_by_id = AsyncMock(return_value=event)

    with pytest.raises(ForbiddenException):
        await service.delete(event.id, uuid.uuid4())
