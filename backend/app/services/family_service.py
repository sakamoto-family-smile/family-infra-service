import secrets
import string
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.family import Family
from app.repositories.family_repository import FamilyRepository
from app.schemas.family import FamilyCreate, FamilyUpdate


def _generate_invite_code(length: int = 8) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


class FamilyService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = FamilyRepository(db)

    async def _get_unique_invite_code(self) -> str:
        for _ in range(10):
            code = _generate_invite_code()
            existing = await self.repo.get_by_invite_code(code)
            if not existing:
                return code
        raise ConflictException("Failed to generate unique invite code")

    async def create(self, data: FamilyCreate) -> Family:
        code = await self._get_unique_invite_code()
        family = Family(
            name=data.name,
            invite_code=code,
            icon_url=data.icon_url,
        )
        return await self.repo.create(family)

    async def get(self, family_id: uuid.UUID) -> Family:
        family = await self.repo.get_by_id(family_id)
        if not family:
            raise NotFoundException("Family not found")
        return family

    async def update(self, family_id: uuid.UUID, data: FamilyUpdate) -> Family:
        family = await self.get(family_id)
        if data.name is not None:
            family.name = data.name
        if data.icon_url is not None:
            family.icon_url = data.icon_url
        return await self.repo.update(family)

    async def regenerate_invite_code(self, family_id: uuid.UUID) -> Family:
        family = await self.get(family_id)
        family.invite_code = await self._get_unique_invite_code()
        return await self.repo.update(family)
