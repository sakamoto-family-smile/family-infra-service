"""
Cloud Functions gen2 - Cloud Storage トリガー
イベント: onObjectFinalized (ファイルアップロード完了)

対象パス: avatars/, chat/, families/ 以下の画像ファイル
処理:
  1. 元画像を 800x800 にリサイズして WebP 形式で上書き保存
  2. サムネイル (200x200) を生成して thumbnail.webp として保存
"""

import io
import logging
import os
import sys
from pathlib import Path

# shared モジュールを参照できるようにルートパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from firebase_functions import storage_fn
from google.cloud import storage as gcs

try:
    from PIL import Image
except ImportError:
    Image = None  # テスト環境などで Pillow が未インストールの場合

logger = logging.getLogger(__name__)

# 処理対象のプレフィックス
TARGET_PREFIXES = ("avatars/", "chat/", "families/")

# リサイズサイズ
MAIN_SIZE = (800, 800)
THUMBNAIL_SIZE = (200, 200)

# 処理済みファイルの識別子 (無限ループ防止)
PROCESSED_SUFFIX = "_resized"
THUMBNAIL_FILENAME = "thumbnail.webp"

# 対応する画像 MIME タイプ
SUPPORTED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/bmp",
    "image/tiff",
}


@storage_fn.on_object_finalized()
def on_image_uploaded(event: storage_fn.CloudEvent[storage_fn.StorageObjectData]) -> None:
    """
    Cloud Storage にファイルがアップロードされたときに呼び出される Cloud Functions。
    対象パスの画像ファイルをリサイズして WebP 形式で保存する。
    """
    if Image is None:
        logger.error("Pillow is not installed. Cannot process images.")
        return

    obj: storage_fn.StorageObjectData = event.data
    bucket_name: str = obj.bucket
    file_path: str = obj.name or ""
    content_type: str = obj.content_type or ""

    logger.info("on_image_uploaded: bucket=%s, path=%s", bucket_name, file_path)

    # 対象プレフィックスの確認
    if not any(file_path.startswith(prefix) for prefix in TARGET_PREFIXES):
        logger.info("Skipping: path does not match target prefixes (%s)", file_path)
        return

    # 処理済みファイルをスキップ (無限ループ防止)
    file_stem = Path(file_path).stem
    if file_stem.endswith(PROCESSED_SUFFIX):
        logger.info("Skipping already-processed file: %s", file_path)
        return
    if Path(file_path).name == THUMBNAIL_FILENAME:
        logger.info("Skipping thumbnail file: %s", file_path)
        return

    # 画像 MIME タイプの確認
    if content_type not in SUPPORTED_CONTENT_TYPES:
        logger.info(
            "Skipping: unsupported content type '%s' for file '%s'", content_type, file_path
        )
        return

    storage_client = gcs.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)

    # 元画像をメモリに読み込む
    try:
        image_bytes = blob.download_as_bytes()
    except Exception as exc:
        logger.error("Failed to download image from GCS (%s): %s", file_path, exc)
        return

    try:
        original_image = Image.open(io.BytesIO(image_bytes))
        # EXIF 情報に基づいて回転を補正
        original_image = _apply_exif_rotation(original_image)
        # RGBA など透過チャンネルを持つ場合は RGB に変換 (WebP でも透過対応だが統一)
        if original_image.mode not in ("RGB", "RGBA"):
            original_image = original_image.convert("RGB")
    except Exception as exc:
        logger.error("Failed to open image (%s): %s", file_path, exc)
        return

    # ---- メイン画像のリサイズ & WebP 変換 ----
    try:
        resized_image = original_image.copy()
        resized_image.thumbnail(MAIN_SIZE, Image.LANCZOS)

        resized_dir = str(Path(file_path).parent)
        resized_filename = f"{file_stem}{PROCESSED_SUFFIX}.webp"
        resized_path = f"{resized_dir}/{resized_filename}" if resized_dir != "." else resized_filename

        resized_buffer = io.BytesIO()
        resized_image.save(resized_buffer, format="WEBP", quality=85, method=6)
        resized_buffer.seek(0)

        resized_blob = bucket.blob(resized_path)
        resized_blob.upload_from_file(resized_buffer, content_type="image/webp")
        logger.info("Resized image saved: gs://%s/%s", bucket_name, resized_path)
    except Exception as exc:
        logger.error("Failed to save resized image (%s): %s", file_path, exc)
        return

    # ---- サムネイル生成 ----
    try:
        thumbnail_image = original_image.copy()
        thumbnail_image.thumbnail(THUMBNAIL_SIZE, Image.LANCZOS)

        thumbnail_dir = str(Path(file_path).parent)
        thumbnail_path = (
            f"{thumbnail_dir}/{THUMBNAIL_FILENAME}"
            if thumbnail_dir != "."
            else THUMBNAIL_FILENAME
        )

        thumb_buffer = io.BytesIO()
        thumbnail_image.save(thumb_buffer, format="WEBP", quality=80, method=6)
        thumb_buffer.seek(0)

        thumbnail_blob = bucket.blob(thumbnail_path)
        thumbnail_blob.upload_from_file(thumb_buffer, content_type="image/webp")
        logger.info("Thumbnail saved: gs://%s/%s", bucket_name, thumbnail_path)
    except Exception as exc:
        logger.error("Failed to save thumbnail (%s): %s", file_path, exc)
        return

    logger.info(
        "Image processing complete for %s: resized=%s, thumbnail=%s",
        file_path,
        resized_path,
        thumbnail_path,
    )


def _apply_exif_rotation(image: "Image.Image") -> "Image.Image":
    """EXIF の Orientation 情報に基づいて画像を回転補正する。"""
    try:
        from PIL import ExifTags

        exif = image.getexif()
        if exif is None:
            return image

        orientation_key = next(
            (k for k, v in ExifTags.TAGS.items() if v == "Orientation"), None
        )
        if orientation_key is None:
            return image

        orientation = exif.get(orientation_key)
        rotation_map = {
            3: 180,
            6: 270,
            8: 90,
        }
        if orientation in rotation_map:
            image = image.rotate(rotation_map[orientation], expand=True)
    except Exception:
        pass  # EXIF 処理に失敗しても続行
    return image
