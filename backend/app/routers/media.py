from fastapi import APIRouter, Form, UploadFile

from app.core.dependencies import CurrentUser, DBSession
from app.schemas.media import MediaContextType, MediaUploadResponse
from app.services.media_service import MediaService

router = APIRouter()


@router.post("/upload", response_model=MediaUploadResponse, status_code=201)
async def upload_media(
    file: UploadFile,
    context_type: MediaContextType = Form(...),
    context_id: str | None = Form(None),
    db: DBSession = ...,
    current_user: CurrentUser = ...,
) -> MediaUploadResponse:
    service = MediaService(db)
    return await service.upload(
        family_id=current_user.family_id,
        uploaded_by=current_user.id,
        file=file,
        context_type=context_type,
        context_id=context_id,
    )
