import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.domain.auth import AuthenticatedUser, UserRole
from app.models.entities import AuditEvent, Dataset, DatasetStatus
from app.schemas.datasets import DatasetResponse
from app.security import require_roles
from app.services.dataset_uploads import (
    DuplicateDatasetError,
    LocalDatasetStorage,
    UploadValidationError,
)

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.post("", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    name: Annotated[str, Form(min_length=1, max_length=255)],
    file: Annotated[UploadFile, File()],
    actor: Annotated[AuthenticatedUser, Depends(require_roles(UserRole.ADMIN))],
    session: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DatasetResponse:
    content = await file.read(settings.max_upload_bytes + 1)
    storage = LocalDatasetStorage(Path(settings.upload_directory), settings.max_upload_bytes)
    try:
        stored = storage.store(file.filename or "", file.content_type, content)
    except DuplicateDatasetError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except UploadValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    dataset = Dataset(
        name=name,
        original_filename=stored.original_filename,
        storage_path=stored.storage_path,
        uploaded_by=uuid.UUID(actor.id),
        upload_status=DatasetStatus.UPLOADED,
        schema_version="1.0",
        validation_summary_json={"size_bytes": stored.size_bytes, "sha256": stored.sha256},
    )
    session.add(dataset)
    session.flush()
    session.add(
        AuditEvent(
            actor_id=uuid.UUID(actor.id),
            event_type="DATASET_UPLOADED",
            entity_type="dataset",
            entity_id=dataset.id,
            before_json=None,
            after_json={"filename": stored.original_filename, "sha256": stored.sha256},
            correlation_id=str(uuid.uuid4()),
        )
    )
    session.commit()
    session.refresh(dataset)
    return DatasetResponse.model_validate(dataset, from_attributes=True)
