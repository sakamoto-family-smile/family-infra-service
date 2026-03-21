import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media_file import MediaFile


class MediaFileRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, file_id: uuid.UUID) -> MediaFile | None:
        result = await self.db.execute(
            select(MediaFile).where(MediaFile.id == file_id)
        )
        return result.scalar_one_or_none()

    async def list_by_family(self, family_id: uuid.UUID) -> list[MediaFile]:
        result = await self.db.execute(
            select(MediaFile)
            .where(MediaFile.family_id == family_id)
            .order_by(MediaFile.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, media_file: MediaFile) -> MediaFile:
        self.db.add(media_file)
        await self.db.flush()
        await self.db.refresh(media_file)
        return media_file

    async def delete(self, media_file: MediaFile) -> None:
        await self.db.delete(media_file)
        await self.db.flush()
