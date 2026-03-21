import uuid

from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser, DBSession
from app.schemas.calendar_event import (
    CalendarEventCreate,
    CalendarEventResponse,
    CalendarEventUpdate,
)
from app.services.calendar_service import CalendarService

router = APIRouter()


@router.post("/{family_id}/events", response_model=CalendarEventResponse, status_code=201)
async def create_event(
    family_id: uuid.UUID,
    data: CalendarEventCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> CalendarEventResponse:
    service = CalendarService(db)
    event = await service.create(family_id, current_user.id, data)
    return CalendarEventResponse.model_validate(event)


@router.get("/{family_id}/events", response_model=list[CalendarEventResponse])
async def list_events(
    family_id: uuid.UUID,
    db: DBSession,
    current_user: CurrentUser,
    start: str | None = Query(None, description="ISO8601 datetime"),
    end: str | None = Query(None, description="ISO8601 datetime"),
) -> list[CalendarEventResponse]:
    service = CalendarService(db)
    events = await service.list_by_family(family_id, start, end)
    return [CalendarEventResponse.model_validate(e) for e in events]


@router.get("/{family_id}/events/{event_id}", response_model=CalendarEventResponse)
async def get_event(
    family_id: uuid.UUID,
    event_id: uuid.UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> CalendarEventResponse:
    service = CalendarService(db)
    event = await service.get(event_id)
    return CalendarEventResponse.model_validate(event)


@router.patch("/{family_id}/events/{event_id}", response_model=CalendarEventResponse)
async def update_event(
    family_id: uuid.UUID,
    event_id: uuid.UUID,
    data: CalendarEventUpdate,
    db: DBSession,
    current_user: CurrentUser,
) -> CalendarEventResponse:
    service = CalendarService(db)
    event = await service.update(event_id, family_id, data)
    return CalendarEventResponse.model_validate(event)


@router.delete("/{family_id}/events/{event_id}", status_code=204)
async def delete_event(
    family_id: uuid.UUID,
    event_id: uuid.UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    service = CalendarService(db)
    await service.delete(event_id, family_id)
