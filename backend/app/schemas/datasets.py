import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.entities import DatasetStatus


class DatasetResponse(BaseModel):
    id: uuid.UUID
    name: str
    original_filename: str
    upload_status: DatasetStatus
    schema_version: str
    created_at: datetime
