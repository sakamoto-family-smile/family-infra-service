from datetime import datetime, timezone

import firebase_admin.auth
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenVerifyResponse


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    async def verify_token(self, id_token: str) -> TokenVerifyResponse:
        try:
            decoded = firebase_admin.auth.verify_id_token(id_token)
        except Exception as e:
            raise UnauthorizedException(f"Token verification failed: {e}")

        return TokenVerifyResponse(
            uid=decoded["uid"],
            email=decoded.get("email"),
            display_name=decoded.get("name"),
        )

    async def update_last_login(self, firebase_uid: str) -> User | None:
        user = await self.user_repo.get_by_firebase_uid(firebase_uid)
        if user:
            user.last_login_at = datetime.now(tz=timezone.utc).replace(tzinfo=None)
            await self.user_repo.update(user)
        return user
