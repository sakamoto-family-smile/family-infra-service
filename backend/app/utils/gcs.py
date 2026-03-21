import asyncio
from datetime import timedelta

from google.cloud import storage


class GCSClient:
    def __init__(self, bucket_name: str) -> None:
        self.bucket_name = bucket_name
        self._client = storage.Client()

    def _get_bucket(self) -> storage.Bucket:
        return self._client.bucket(self.bucket_name)

    async def upload(self, path: str, data: bytes, content_type: str) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._upload_sync, path, data, content_type)

    def _upload_sync(self, path: str, data: bytes, content_type: str) -> None:
        bucket = self._get_bucket()
        blob = bucket.blob(path)
        blob.upload_from_string(data, content_type=content_type)

    async def get_signed_url(self, path: str, expires_in: int = 3600) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._signed_url_sync, path, expires_in
        )

    def _signed_url_sync(self, path: str, expires_in: int) -> str:
        bucket = self._get_bucket()
        blob = bucket.blob(path)
        return blob.generate_signed_url(
            expiration=timedelta(seconds=expires_in),
            method="GET",
            version="v4",
        )

    async def delete(self, path: str) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._delete_sync, path)

    def _delete_sync(self, path: str) -> None:
        bucket = self._get_bucket()
        blob = bucket.blob(path)
        blob.delete(if_generation_match=None)
