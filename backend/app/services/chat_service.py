import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.chat_room import ChatRoom
from app.repositories.chat_room_repository import ChatRoomRepository
from app.schemas.chat_room import ChatRoomCreate, ChatRoomUpdate


class ChatService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = ChatRoomRepository(db)

    async def create_room(
        self, family_id: uuid.UUID, created_by: uuid.UUID, data: ChatRoomCreate
    ) -> ChatRoom:
        room = ChatRoom(
            family_id=family_id,
            name=data.name,
            type=data.type,
            created_by=created_by,
        )
        return await self.repo.create(room)

    async def get(self, room_id: uuid.UUID) -> ChatRoom:
        room = await self.repo.get_by_id(room_id)
        if not room:
            raise NotFoundException("Chat room not found")
        return room

    async def list_by_family(self, family_id: uuid.UUID) -> list[ChatRoom]:
        return await self.repo.list_by_family(family_id)

    async def update(
        self,
        room_id: uuid.UUID,
        family_id: uuid.UUID,
        data: ChatRoomUpdate,
    ) -> ChatRoom:
        room = await self.get(room_id)
        if str(room.family_id) != str(family_id):
            raise ForbiddenException("Room does not belong to this family")
        if data.name is not None:
            room.name = data.name
        return await self.repo.update(room)

    async def delete(self, room_id: uuid.UUID, family_id: uuid.UUID) -> None:
        room = await self.get(room_id)
        if str(room.family_id) != str(family_id):
            raise ForbiddenException("Room does not belong to this family")
        await self.repo.delete(room)
