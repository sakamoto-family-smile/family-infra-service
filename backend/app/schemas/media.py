import uuid
from datetime import datetime

from pydantic import BaseModel, Field

MediaContextType = str  # 'avatar' | 'chat' | 'family_icon' | 'export'


class MediaUploadResponse(BaseModel):
    id: uuid.UUID
    gcs_path: str
    file_name: str
    content_type: str
    file_size_bytes: int
    context_type: MediaContextType
    context_id: str | None
    signed_url: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SignedUrlRequest(BaseModel):
    gcs_path: str = Field(..., description="GCS path of the file")
    expires_in: int = Field(default=3600, ge=60, le=86400)
