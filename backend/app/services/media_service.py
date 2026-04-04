import uuid
from datetime import datetime, timezone
from typing import cast

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import BadRequestException
from app.models.media_file import MediaFile
from app.repositories.media_file_repository import MediaFileRepository
from app.schemas.media import MediaContextType, MediaUploadResponse
from app.utils.gcs import GCSClient

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class MediaService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = MediaFileRepository(db)
        self.gcs = GCSClient(settings.GCS_BUCKET)

    def _build_gcs_path(
        self,
        context_type: MediaContextType,
        context_id: str,
        file_name: str,
    ) -> str:
        ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else "bin"
        ts = int(datetime.now(tz=timezone.utc).timestamp())
        match context_type:
            case "avatar":
                return f"avatars/{context_id}/profile.{ext}"
            case "chat":
                return f"chat/{context_id}/{ts}.{ext}"
            case "family_icon":
                return f"families/{context_id}/icon.{ext}"
            case _:
                return f"exports/{context_id}/{ts}.{ext}"

    async def upload(
        self,
        family_id: uuid.UUID,
        uploaded_by: uuid.UUID,
        file: UploadFile,
        context_type: MediaContextType,
        context_id: str | None = None,
    ) -> MediaUploadResponse:
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise BadRequestException(f"Unsupported file type: {file.content_type}")

        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            raise BadRequestException("File size exceeds 10MB limit")

        gcs_path = self._build_gcs_path(
            context_type,
            context_id or str(uploaded_by),
            file.filename or "file",
        )

        await self.gcs.upload(gcs_path, content, file.content_type or "application/octet-stream")

        media = MediaFile(
            family_id=family_id,
            uploaded_by=uploaded_by,
            gcs_path=gcs_path,
            file_name=file.filename or "file",
            content_type=file.content_type or "application/octet-stream",
            file_size_bytes=len(content),
            context_type=context_type,
            context_id=context_id,
        )
        saved = await self.repo.create(media)
        signed_url = await self.gcs.get_signed_url(gcs_path)

        return MediaUploadResponse(
            id=saved.id,
            gcs_path=saved.gcs_path,
            file_name=saved.file_name,
            content_type=saved.content_type,
            file_size_bytes=saved.file_size_bytes,
            context_type=cast(MediaContextType, saved.context_type),
            context_id=saved.context_id,
            signed_url=signed_url,
            created_at=saved.created_at,
        )
