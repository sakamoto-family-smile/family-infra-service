import uuid
from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field

UserRole = str  # 'admin' | 'member' | 'child'


class UserBase(BaseModel):
    display_name: str = Field(..., max_length=50)
    avatar_url: str | None = None
    date_of_birth: date | None = None


class UserCreate(UserBase):
    firebase_uid: str
    email: EmailStr
    family_id: uuid.UUID
    role: UserRole = "member"


class UserUpdate(BaseModel):
    display_name: str | None = Field(None, max_length=50)
    avatar_url: str | None = None
    date_of_birth: date | None = None


class UserResponse(UserBase):
    id: uuid.UUID
    family_id: uuid.UUID
    email: str
    role: UserRole
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
