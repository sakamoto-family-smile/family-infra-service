import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.family import Family


class FamilyRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, family_id: uuid.UUID) -> Family | None:
        result = await self.db.execute(
            select(Family).where(Family.id == family_id)
        )
        return result.scalar_one_or_none()

    async def get_by_invite_code(self, invite_code: str) -> Family | None:
        result = await self.db.execute(
            select(Family).where(Family.invite_code == invite_code)
        )
        return result.scalar_one_or_none()

    async def create(self, family: Family) -> Family:
        self.db.add(family)
        await self.db.flush()
        await self.db.refresh(family)
        return family

    async def update(self, family: Family) -> Family:
        await self.db.flush()
        await self.db.refresh(family)
        return family

    async def delete(self, family: Family) -> None:
        await self.db.delete(family)
        await self.db.flush()
