from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import FirebaseToken
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.db.session import async_session_factory
from app.models.user import User
from app.repositories.user_repository import UserRepository


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


DBSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    token: FirebaseToken,
    db: DBSession,
) -> User:
    firebase_uid = token.get("uid")
    if not firebase_uid:
        raise UnauthorizedException("Invalid token: missing uid")

    repo = UserRepository(db)
    user = await repo.get_by_firebase_uid(firebase_uid)
    if not user:
        raise UnauthorizedException("User not found")
    if not user.is_active:
        raise ForbiddenException("User is inactive")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def require_family_member(
    family_id: str,
    current_user: CurrentUser,
) -> User:
    if str(current_user.family_id) != family_id:
        raise ForbiddenException("Not a member of this family")
    return current_user


async def require_family_admin(
    family_id: str,
    current_user: CurrentUser,
) -> User:
    if str(current_user.family_id) != family_id:
        raise ForbiddenException("Not a member of this family")
    if current_user.role != "admin":
        raise ForbiddenException("Admin role required")
    return current_user
