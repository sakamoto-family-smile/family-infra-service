import uuid
from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, Field


class FamilyBase(BaseModel):
    name: str = Field(..., max_length=100)
    icon_url: AnyHttpUrl | None = None


class FamilyCreate(FamilyBase):
    pass


class FamilyUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    icon_url: AnyHttpUrl | None = None


class FamilyResponse(FamilyBase):
    id: uuid.UUID
    invite_code: str
    plan: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FamilyJoinRequest(BaseModel):
    invite_code: str = Field(..., max_length=20)
