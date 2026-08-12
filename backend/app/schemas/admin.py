import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    actor_id: uuid.UUID | None
    event_type: str
    entity_type: str
    entity_id: uuid.UUID
    correlation_id: str
    created_at: datetime


class AuditListResponse(BaseModel):
    items: list[AuditEventResponse]
    page: int
    page_size: int
    total: int
