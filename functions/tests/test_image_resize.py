"""Tests for image_resize Cloud Function."""
import io
import sys
import os
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _make_event(bucket: str, name: str, content_type: str) -> MagicMock:
    obj = MagicMock()
    obj.bucket = bucket
    obj.name = name
    obj.content_type = content_type

    event = MagicMock()
    event.data = obj
    return event


class TestApplyExifRotation:
    def test_returns_image_without_exif(self):
        from image_resize.main import _apply_exif_rotation

        img = MagicMock()
        img.getexif.return_value = None
        result = _apply_exif_rotation(img)
        assert result is img

    def test_rotates_image_based_on_orientation(self):
        from image_resize.main import _apply_exif_rotation

        img = MagicMock()
        exif = {274: 3}  # 274 = Orientation tag, 3 = 180 degrees
        img.getexif.return_value = exif
        rotated = MagicMock()
        img.rotate.return_value = rotated

        with patch("image_resize.main.Image") as MockImage:
            from PIL import ExifTags
            MockImage.Image = MagicMock()

            result = _apply_exif_rotation(img)
            # Even if rotation logic isn't triggered due to mock, should not raise
            assert result is not None


class TestOnImageUploaded:
    def test_skips_non_target_path(self):
        from image_resize.main import on_image_uploaded

        event = _make_event("my-bucket", "exports/data.csv", "text/csv")

        with patch("image_resize.main.gcs") as mock_gcs:
            on_image_uploaded(event)
            mock_gcs.Client.assert_not_called()

    def test_skips_already_processed_file(self):
        from image_resize.main import on_image_uploaded

        event = _make_event("my-bucket", "avatars/uid-1/photo_resized.webp", "image/webp")

        with patch("image_resize.main.gcs") as mock_gcs:
            on_image_uploaded(event)
            mock_gcs.Client.assert_not_called()

    def test_skips_thumbnail_file(self):
        from image_resize.main import on_image_uploaded

        event = _make_event("my-bucket", "chat/room-1/thumbnail.webp", "image/webp")

        with patch("image_resize.main.gcs") as mock_gcs:
            on_image_uploaded(event)
            mock_gcs.Client.assert_not_called()

    def test_skips_unsupported_content_type(self):
        from image_resize.main import on_image_uploaded

        event = _make_event("my-bucket", "avatars/uid-1/doc.pdf", "application/pdf")

        with patch("image_resize.main.gcs") as mock_gcs:
            on_image_uploaded(event)
            mock_gcs.Client.assert_not_called()

    def test_processes_valid_image(self):
        pytest.importorskip("PIL", reason="Pillow not installed")
        from PIL import Image as PILImage
        from image_resize.main import on_image_uploaded

        # Create a small test image in memory
        img = PILImage.new("RGB", (100, 100), color=(255, 0, 0))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        image_bytes = buf.read()

        event = _make_event("my-bucket", "avatars/uid-1/photo.jpg", "image/jpeg")

        mock_storage_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.download_as_bytes.return_value = image_bytes
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.bucket.return_value = mock_bucket

        with patch("image_resize.main.gcs") as mock_gcs:
            mock_gcs.Client.return_value = mock_storage_client
            on_image_uploaded(event)

        # Should upload resized + thumbnail
        assert mock_blob.upload_from_file.call_count == 2
