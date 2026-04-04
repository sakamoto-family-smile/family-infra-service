import uuid
from datetime import datetime, timezone

from app.models.calendar_event import CalendarEvent


def make_calendar_event(**kwargs) -> CalendarEvent:
    family_id = kwargs.pop("family_id", uuid.uuid4())
    created_by = kwargs.pop("created_by", uuid.uuid4())
    defaults = {
        "id": uuid.uuid4(),
        "family_id": family_id,
        "created_by": created_by,
        "title": "Test Event",
        "start_at": datetime(2024, 6, 1, 10, 0, tzinfo=timezone.utc),
        "end_at": datetime(2024, 6, 1, 11, 0, tzinfo=timezone.utc),
        "is_all_day": False,
    }
    defaults.update(kwargs)
    return CalendarEvent(**defaults)
