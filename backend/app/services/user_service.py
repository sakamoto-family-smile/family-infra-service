import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.user import User
from app.repositories.family_repository import FamilyRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = UserRepository(db)
        self.family_repo = FamilyRepository(db)

    async def create(self, data: UserCreate) -> User:
        existing = await self.repo.get_by_firebase_uid(data.firebase_uid)
        if existing:
            raise ConflictException("User already exists")

        family = await self.family_repo.get_by_id(data.family_id)
        if not family:
            raise NotFoundException("Family not found")

        user = User(
            family_id=data.family_id,
            firebase_uid=data.firebase_uid,
            display_name=data.display_name,
            email=str(data.email),
            avatar_url=data.avatar_url,
            role=data.role,
            date_of_birth=data.date_of_birth,
        )
        return await self.repo.create(user)

    async def get(self, user_id: uuid.UUID) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    async def list_by_family(self, family_id: uuid.UUID) -> list[User]:
        return await self.repo.list_by_family(family_id)

    async def update(self, user_id: uuid.UUID, data: UserUpdate) -> User:
        user = await self.get(user_id)
        if data.display_name is not None:
            user.display_name = data.display_name
        if data.avatar_url is not None:
            user.avatar_url = data.avatar_url
        if data.date_of_birth is not None:
            user.date_of_birth = data.date_of_birth
        return await self.repo.update(user)

    async def deactivate(self, user_id: uuid.UUID) -> None:
        user = await self.get(user_id)
        await self.repo.delete(user)

    async def join_family_by_invite(
        self, invite_code: str, firebase_uid: str, display_name: str, email: str
    ) -> User:
        family = await self.family_repo.get_by_invite_code(invite_code)
        if not family:
            raise NotFoundException("Invalid invite code")

        existing = await self.repo.get_by_firebase_uid(firebase_uid)
        if existing:
            raise ConflictException("User already registered")

        user = User(
            family_id=family.id,
            firebase_uid=firebase_uid,
            display_name=display_name,
            email=email,
            role="member",
        )
        return await self.repo.create(user)
