import uuid

from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DBSession
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/{family_id}/members", response_model=list[UserResponse])
async def list_members(
    family_id: uuid.UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> list[UserResponse]:
    service = UserService(db)
    users = await service.list_by_family(family_id)
    return [UserResponse.model_validate(u) for u in users]


@router.get("/{family_id}/members/{user_id}", response_model=UserResponse)
async def get_member(
    family_id: uuid.UUID,
    user_id: uuid.UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> UserResponse:
    service = UserService(db)
    user = await service.get(user_id)
    return UserResponse.model_validate(user)


@router.patch("/{family_id}/members/{user_id}", response_model=UserResponse)
async def update_member(
    family_id: uuid.UUID,
    user_id: uuid.UUID,
    data: UserUpdate,
    db: DBSession,
    current_user: CurrentUser,
) -> UserResponse:
    service = UserService(db)
    user = await service.update(user_id, data)
    return UserResponse.model_validate(user)


@router.delete("/{family_id}/members/{user_id}", status_code=204)
async def remove_member(
    family_id: uuid.UUID,
    user_id: uuid.UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    service = UserService(db)
    await service.deactivate(user_id)
