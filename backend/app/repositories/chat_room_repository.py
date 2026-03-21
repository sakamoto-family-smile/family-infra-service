import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_room import ChatRoom


class ChatRoomRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, room_id: uuid.UUID) -> ChatRoom | None:
        result = await self.db.execute(
            select(ChatRoom).where(ChatRoom.id == room_id)
        )
        return result.scalar_one_or_none()

    async def list_by_family(self, family_id: uuid.UUID) -> list[ChatRoom]:
        result = await self.db.execute(
            select(ChatRoom)
            .where(ChatRoom.family_id == family_id)
            .order_by(ChatRoom.last_message_at.desc().nullslast())
        )
        return list(result.scalars().all())

    async def create(self, room: ChatRoom) -> ChatRoom:
        self.db.add(room)
        await self.db.flush()
        await self.db.refresh(room)
        return room

    async def update(self, room: ChatRoom) -> ChatRoom:
        await self.db.flush()
        await self.db.refresh(room)
        return room

    async def delete(self, room: ChatRoom) -> None:
        await self.db.delete(room)
        await self.db.flush()
