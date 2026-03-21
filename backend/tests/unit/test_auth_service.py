from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import UnauthorizedException
from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_verify_token_success():
    db = MagicMock()
    service = AuthService(db)

    with patch("firebase_admin.auth.verify_id_token") as mock_verify:
        mock_verify.return_value = {
            "uid": "test-uid",
            "email": "test@example.com",
            "name": "Test User",
        }
        result = await service.verify_token("valid-token")
        assert result.uid == "test-uid"
        assert result.email == "test@example.com"


@pytest.mark.asyncio
async def test_verify_token_invalid():
    db = MagicMock()
    service = AuthService(db)

    with patch("firebase_admin.auth.verify_id_token") as mock_verify:
        mock_verify.side_effect = Exception("Invalid token")
        with pytest.raises(UnauthorizedException):
            await service.verify_token("invalid-token")


@pytest.mark.asyncio
async def test_update_last_login():
    from tests.factories.user_factory import make_user

    db = MagicMock()
    service = AuthService(db)
    user = make_user(firebase_uid="test-uid")

    service.user_repo.get_by_firebase_uid = AsyncMock(return_value=user)
    service.user_repo.update = AsyncMock(return_value=user)

    result = await service.update_last_login("test-uid")
    assert result is not None
    assert result.last_login_at is not None
