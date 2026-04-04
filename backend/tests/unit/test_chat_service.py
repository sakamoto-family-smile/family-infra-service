import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import ForbiddenException, NotFoundException
from app.schemas.chat_room import ChatRoomCreate, ChatRoomUpdate
from app.services.chat_service import ChatService
from tests.factories.chat_room_factory import make_chat_room


@pytest.mark.asyncio
async def test_create_room():
    db = MagicMock()
    service = ChatService(db)
    family_id = uuid.uuid4()
    created_by = uuid.uuid4()
    room = make_chat_room(family_id=family_id, created_by=created_by, name="Family Chat")

    service.repo.create = AsyncMock(return_value=room)

    result = await service.create_room(
        family_id, created_by, ChatRoomCreate(name="Family Chat", type="general")
    )
    assert result.name == "Family Chat"
    service.repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_get_room_not_found():
    db = MagicMock()
    service = ChatService(db)
    service.repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException):
        await service.get(uuid.uuid4())


@pytest.mark.asyncio
async def test_get_room_success():
    db = MagicMock()
    service = ChatService(db)
    room = make_chat_room(name="My Room")
    service.repo.get_by_id = AsyncMock(return_value=room)

    result = await service.get(room.id)
    assert result.name == "My Room"


@pytest.mark.asyncio
async def test_list_by_family():
    db = MagicMock()
    service = ChatService(db)
    family_id = uuid.uuid4()
    rooms = [make_chat_room(family_id=family_id), make_chat_room(family_id=family_id)]
    service.repo.list_by_family = AsyncMock(return_value=rooms)

    result = await service.list_by_family(family_id)
    assert len(result) == 2


@pytest.mark.asyncio
async def test_update_room_success():
    db = MagicMock()
    service = ChatService(db)
    family_id = uuid.uuid4()
    room = make_chat_room(family_id=family_id, name="Old Name")
    room.name = "New Name"

    service.repo.get_by_id = AsyncMock(return_value=room)
    service.repo.update = AsyncMock(return_value=room)

    result = await service.update(room.id, family_id, ChatRoomUpdate(name="New Name"))
    assert result.name == "New Name"


@pytest.mark.asyncio
async def test_update_room_wrong_family():
    db = MagicMock()
    service = ChatService(db)
    room = make_chat_room(family_id=uuid.uuid4())
    service.repo.get_by_id = AsyncMock(return_value=room)

    with pytest.raises(ForbiddenException):
        await service.update(room.id, uuid.uuid4(), ChatRoomUpdate(name="Hack"))


@pytest.mark.asyncio
async def test_delete_room_success():
    db = MagicMock()
    service = ChatService(db)
    family_id = uuid.uuid4()
    room = make_chat_room(family_id=family_id)

    service.repo.get_by_id = AsyncMock(return_value=room)
    service.repo.delete = AsyncMock(return_value=None)

    await service.delete(room.id, family_id)
    service.repo.delete.assert_called_once_with(room)


@pytest.mark.asyncio
async def test_delete_room_wrong_family():
    db = MagicMock()
    service = ChatService(db)
    room = make_chat_room(family_id=uuid.uuid4())
    service.repo.get_by_id = AsyncMock(return_value=room)

    with pytest.raises(ForbiddenException):
        await service.delete(room.id, uuid.uuid4())
