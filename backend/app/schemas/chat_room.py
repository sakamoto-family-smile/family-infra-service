import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ChatRoomType = Literal["family", "direct", "group"]


class ChatRoomBase(BaseModel):
    name: str = Field(..., max_length=100)
    type: ChatRoomType


class ChatRoomCreate(ChatRoomBase):
    pass


class ChatRoomUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)


class ChatRoomResponse(ChatRoomBase):
    id: uuid.UUID
    family_id: uuid.UUID
    created_by: uuid.UUID
    last_message_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
