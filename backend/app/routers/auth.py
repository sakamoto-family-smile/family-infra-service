from fastapi import APIRouter

from app.core.auth import FirebaseToken
from app.core.dependencies import DBSession
from app.schemas.auth import TokenVerifyResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/verify", response_model=TokenVerifyResponse)
async def verify_token(token: FirebaseToken, db: DBSession) -> TokenVerifyResponse:
    service = AuthService(db)
    await service.update_last_login(token["uid"])
    return TokenVerifyResponse(
        uid=token["uid"],
        email=token.get("email"),
        display_name=token.get("name"),
    )
