import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_verify_token(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/verify",
        headers={"Authorization": "Bearer valid-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["uid"] == "test-firebase-uid"
    assert data["email"] == "test@example.com"
