import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from tests.factories.family_factory import make_family
from tests.factories.user_factory import make_user


@pytest.mark.asyncio
async def test_get_family(client: AsyncClient, db_session):
    family = make_family()
    user = make_user(family_id=family.id, firebase_uid="test-firebase-uid")
    db_session.add(family)
    db_session.add(user)

    with patch(
        "app.repositories.family_repository.FamilyRepository.get_by_id",
        new_callable=AsyncMock,
        return_value=family,
    ):
        response = await client.get(
            f"/api/v1/families/{family.id}",
            headers={"Authorization": "Bearer valid-token"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == family.name
