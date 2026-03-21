import uuid

from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DBSession
from app.schemas.family import FamilyCreate, FamilyResponse, FamilyUpdate
from app.services.family_service import FamilyService

router = APIRouter()


@router.post("", response_model=FamilyResponse, status_code=201)
async def create_family(
    data: FamilyCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> FamilyResponse:
    service = FamilyService(db)
    family = await service.create(data)
    return FamilyResponse.model_validate(family)


@router.get("/{family_id}", response_model=FamilyResponse)
async def get_family(
    family_id: uuid.UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> FamilyResponse:
    service = FamilyService(db)
    family = await service.get(family_id)
    return FamilyResponse.model_validate(family)


@router.patch("/{family_id}", response_model=FamilyResponse)
async def update_family(
    family_id: uuid.UUID,
    data: FamilyUpdate,
    db: DBSession,
    current_user: CurrentUser,
) -> FamilyResponse:
    service = FamilyService(db)
    family = await service.update(family_id, data)
    return FamilyResponse.model_validate(family)


@router.post("/{family_id}/regenerate-invite", response_model=FamilyResponse)
async def regenerate_invite_code(
    family_id: uuid.UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> FamilyResponse:
    service = FamilyService(db)
    family = await service.regenerate_invite_code(family_id)
    return FamilyResponse.model_validate(family)
