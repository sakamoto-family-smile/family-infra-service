import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import ConflictException, NotFoundException
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import UserService
from tests.factories.family_factory import make_family
from tests.factories.user_factory import make_user


@pytest.mark.asyncio
async def test_create_user_success():
    db = MagicMock()
    service = UserService(db)
    family = make_family()
    user = make_user(family_id=family.id, firebase_uid="new-uid")

    service.repo.get_by_firebase_uid = AsyncMock(return_value=None)
    service.family_repo.get_by_id = AsyncMock(return_value=family)
    service.repo.create = AsyncMock(return_value=user)

    data = UserCreate(
        family_id=family.id,
        firebase_uid="new-uid",
        display_name="Taro",
        email="taro@example.com",
        role="member",
    )
    result = await service.create(data)
    assert result.firebase_uid == "new-uid"


@pytest.mark.asyncio
async def test_create_user_already_exists():
    db = MagicMock()
    service = UserService(db)
    existing_user = make_user(firebase_uid="existing-uid")

    service.repo.get_by_firebase_uid = AsyncMock(return_value=existing_user)

    with pytest.raises(ConflictException):
        await service.create(
            UserCreate(
                family_id=uuid.uuid4(),
                firebase_uid="existing-uid",
                display_name="Taro",
                email="taro@example.com",
                role="member",
            )
        )


@pytest.mark.asyncio
async def test_create_user_family_not_found():
    db = MagicMock()
    service = UserService(db)

    service.repo.get_by_firebase_uid = AsyncMock(return_value=None)
    service.family_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException):
        await service.create(
            UserCreate(
                family_id=uuid.uuid4(),
                firebase_uid="uid-x",
                display_name="Taro",
                email="taro@example.com",
                role="member",
            )
        )


@pytest.mark.asyncio
async def test_get_user_not_found():
    db = MagicMock()
    service = UserService(db)
    service.repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException):
        await service.get(uuid.uuid4())


@pytest.mark.asyncio
async def test_update_user():
    db = MagicMock()
    service = UserService(db)
    user = make_user(display_name="Old Name")
    user.display_name = "New Name"

    service.repo.get_by_id = AsyncMock(return_value=user)
    service.repo.update = AsyncMock(return_value=user)

    result = await service.update(user.id, UserUpdate(display_name="New Name"))
    assert result.display_name == "New Name"


@pytest.mark.asyncio
async def test_join_family_by_invite_success():
    db = MagicMock()
    service = UserService(db)
    family = make_family()
    user = make_user(family_id=family.id, firebase_uid="join-uid")

    service.family_repo.get_by_invite_code = AsyncMock(return_value=family)
    service.repo.get_by_firebase_uid = AsyncMock(return_value=None)
    service.repo.create = AsyncMock(return_value=user)

    result = await service.join_family_by_invite(
        invite_code="INVITE123",
        firebase_uid="join-uid",
        display_name="New Member",
        email="new@example.com",
    )
    assert result.firebase_uid == "join-uid"


@pytest.mark.asyncio
async def test_join_family_invalid_invite_code():
    db = MagicMock()
    service = UserService(db)
    service.family_repo.get_by_invite_code = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException):
        await service.join_family_by_invite(
            invite_code="INVALID",
            firebase_uid="uid-x",
            display_name="Someone",
            email="x@example.com",
        )


@pytest.mark.asyncio
async def test_join_family_user_already_registered():
    db = MagicMock()
    service = UserService(db)
    family = make_family()
    existing_user = make_user()

    service.family_repo.get_by_invite_code = AsyncMock(return_value=family)
    service.repo.get_by_firebase_uid = AsyncMock(return_value=existing_user)

    with pytest.raises(ConflictException):
        await service.join_family_by_invite(
            invite_code="CODE",
            firebase_uid="existing-uid",
            display_name="Dup",
            email="dup@example.com",
        )
