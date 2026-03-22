import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.media_service import MediaService


def _make_upload_file(filename: str = "test.jpg", content_type: str = "image/jpeg") -> MagicMock:
    f = MagicMock()
    f.filename = filename
    f.content_type = content_type
    f.read = AsyncMock(return_value=b"fake-image-data")
    return f


@pytest.mark.asyncio
async def test_build_gcs_path_avatar():
    with patch("app.services.media_service.GCSClient"):
        service = MediaService(MagicMock())

    path = service._build_gcs_path("avatar", "user-123", "photo.jpg")
    assert path.startswith("avatars/user-123/")
    assert path.endswith(".jpg")


@pytest.mark.asyncio
async def test_build_gcs_path_chat():
    with patch("app.services.media_service.GCSClient"):
        service = MediaService(MagicMock())

    path = service._build_gcs_path("chat", "room-456", "image.png")
    assert path.startswith("chat/room-456/")
    assert path.endswith(".png")


@pytest.mark.asyncio
async def test_build_gcs_path_family_icon():
    with patch("app.services.media_service.GCSClient"):
        service = MediaService(MagicMock())

    path = service._build_gcs_path("family_icon", "fam-789", "icon.webp")
    assert path.startswith("families/fam-789/")
    assert path.endswith(".webp")


@pytest.mark.asyncio
async def test_upload_success():
    db = MagicMock()

    with patch("app.services.media_service.GCSClient") as mock_gcs_class:
        mock_gcs_instance = MagicMock()
        mock_gcs_instance.upload = AsyncMock()
        mock_gcs_instance.get_signed_url = AsyncMock(return_value="https://signed.url/file")
        mock_gcs_class.return_value = mock_gcs_instance

        service = MediaService(db)

    family_id = uuid.uuid4()
    user_id = uuid.uuid4()
    file = _make_upload_file()

    mock_media = MagicMock()
    mock_media.id = uuid.uuid4()
    mock_media.gcs_path = "avatars/test/profile.jpg"
    mock_media.file_name = "test.jpg"
    mock_media.content_type = "image/jpeg"
    mock_media.file_size_bytes = 15
    mock_media.context_type = "avatar"
    mock_media.context_id = None
    mock_media.created_at = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    service.repo.create = AsyncMock(return_value=mock_media)

    result = await service.upload(
        family_id=family_id,
        uploaded_by=user_id,
        file=file,
        context_type="avatar",
    )

    assert result.gcs_path == "avatars/test/profile.jpg"
    assert result.signed_url == "https://signed.url/file"
    service.gcs.upload.assert_called_once()
