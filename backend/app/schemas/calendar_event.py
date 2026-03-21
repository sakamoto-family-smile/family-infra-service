import uuid
from datetime import datetime

from pydantic import BaseModel, Field, model_validator

AttendeeStatus = str  # 'accepted' | 'declined' | 'tentative'


class AttendeeCreate(BaseModel):
    user_id: uuid.UUID


class AttendeeResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    status: AttendeeStatus
    responded_at: datetime | None

    model_config = {"from_attributes": True}


class CalendarEventBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: str | None = None
    start_at: datetime
    end_at: datetime
    is_all_day: bool = False
    location: str | None = Field(None, max_length=300)
    color: str | None = Field(None, max_length=7)
    recurrence_rule: str | None = Field(None, max_length=255)
    reminder_minutes: int | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "CalendarEventBase":
        if self.end_at <= self.start_at:
            raise ValueError("end_at must be after start_at")
        return self


class CalendarEventCreate(CalendarEventBase):
    attendee_ids: list[uuid.UUID] = Field(default_factory=list)


class CalendarEventUpdate(BaseModel):
    title: str | None = Field(None, max_length=200)
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    is_all_day: bool | None = None
    location: str | None = None
    color: str | None = None
    recurrence_rule: str | None = None
    reminder_minutes: int | None = None


class CalendarEventResponse(CalendarEventBase):
    id: uuid.UUID
    family_id: uuid.UUID
    created_by: uuid.UUID
    attendees: list[AttendeeResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
