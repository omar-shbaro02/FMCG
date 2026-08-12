import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.domain.auth import AuthenticatedUser, UserRole
from app.domain.data_quality import DatasetValidator
from app.models.entities import AuditEvent, Dataset, DatasetStatus, DatasetValidationIssue
from app.schemas.datasets import (
    DatasetResponse,
    DatasetValidationRequest,
    DatasetValidationResponse,
)
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


@router.post(
    "/{dataset_id}/validate",
    response_model=DatasetValidationResponse,
    status_code=status.HTTP_200_OK,
)
def validate_dataset(
    dataset_id: uuid.UUID,
    request: DatasetValidationRequest,
    actor: Annotated[AuthenticatedUser, Depends(require_roles(UserRole.ADMIN))],
    session: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DatasetValidationResponse:
    dataset = session.get(Dataset, dataset_id)
    if dataset is None or dataset.upload_status == DatasetStatus.ARCHIVED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    source = Path(dataset.storage_path)
    if not source.is_file():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Uploaded dataset file is unavailable",
        )

    previous_status = dataset.upload_status
    dataset.upload_status = DatasetStatus.VALIDATING
    session.flush()
    report = DatasetValidator(settings.minimum_history_weeks).validate(
        source,
        currency=request.currency,
        gross_margin_representation=request.gross_margin_representation,
        stock_unit=request.stock_unit,
    )
    if report.has_critical_errors:
        final_status = DatasetStatus.INVALID
    elif report.has_warnings:
        final_status = DatasetStatus.VALID_WITH_WARNINGS
    else:
        final_status = DatasetStatus.VALID

    summary = report.as_dict()
    summary["dataset_id"] = str(dataset.id)
    summary["overall_status"] = final_status.value
    dataset.upload_status = final_status
    dataset.row_count = report.row_count
    dataset.date_min = report.date_min
    dataset.date_max = report.date_max
    dataset.validation_summary_json = summary
    session.execute(
        delete(DatasetValidationIssue).where(DatasetValidationIssue.dataset_id == dataset.id)
    )
    session.add_all(
        [
            DatasetValidationIssue(
                dataset_id=dataset.id,
                severity=issue.severity,
                field_name=issue.field_name,
                row_reference=issue.row_reference,
                issue_code=issue.issue_code,
                issue_message=issue.issue_message,
                resolution_status="OPEN",
            )
            for issue in report.issues
        ]
    )
    session.add(
        AuditEvent(
            actor_id=uuid.UUID(actor.id),
            event_type="DATASET_VALIDATED",
            entity_type="dataset",
            entity_id=dataset.id,
            before_json={"status": previous_status.value},
            after_json={
                "status": final_status.value,
                "critical_error_count": len(summary["critical_errors"]),
                "warning_count": len(summary["warnings"]),
            },
            correlation_id=str(uuid.uuid4()),
        )
    )
    session.commit()
    return DatasetValidationResponse.model_validate(summary)


@router.get(
    "/{dataset_id}/validation",
    response_model=DatasetValidationResponse,
)
def get_dataset_validation(
    dataset_id: uuid.UUID,
    _: Annotated[
        AuthenticatedUser,
        Depends(require_roles(UserRole.ADMIN, UserRole.COMMERCIAL_DIRECTOR)),
    ],
    session: Annotated[Session, Depends(get_db)],
) -> DatasetValidationResponse:
    dataset = session.get(Dataset, dataset_id)
    if dataset is None or not dataset.validation_summary_json.get("overall_status"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset validation report not found",
        )
    return DatasetValidationResponse.model_validate(dataset.validation_summary_json)
