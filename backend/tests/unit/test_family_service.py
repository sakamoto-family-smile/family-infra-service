from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import NotFoundException
from app.schemas.family import FamilyCreate, FamilyUpdate
from app.services.family_service import FamilyService
from tests.factories.family_factory import make_family


@pytest.mark.asyncio
async def test_create_family():
    db = MagicMock()
    service = FamilyService(db)

    family = make_family(name="Tanaka Family")
    service.repo.get_by_invite_code = AsyncMock(return_value=None)
    service.repo.create = AsyncMock(return_value=family)

    result = await service.create(FamilyCreate(name="Tanaka Family"))
    assert result.name == "Tanaka Family"
    service.repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_get_family_not_found():
    import uuid

    db = MagicMock()
    service = FamilyService(db)
    service.repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException):
        await service.get(uuid.uuid4())


@pytest.mark.asyncio
async def test_update_family():
    import uuid

    db = MagicMock()
    service = FamilyService(db)
    family = make_family(name="Old Name")

    service.repo.get_by_id = AsyncMock(return_value=family)
    service.repo.update = AsyncMock(return_value=family)

    result = await service.update(family.id, FamilyUpdate(name="New Name"))
    assert result.name == "New Name"
