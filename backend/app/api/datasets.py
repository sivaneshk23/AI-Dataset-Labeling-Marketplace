"""Dataset management and file-upload endpoints."""

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_current_user, require_roles
from backend.app.core.database import get_db
from backend.app.core.errors import NotFoundError
from backend.app.core.roles import ADMINISTRATOR, DATASET_OWNER
from backend.app.models.user import User
from backend.app.schemas.dataset import (
    DatasetCreate,
    DatasetResponse,
    DatasetUploadResponse,
)
from backend.app.schemas.response import APIResponse, success_response
from backend.app.services.dataset_import_service import DatasetImportService
from backend.app.services.dataset_service import DatasetService

router = APIRouter(prefix="/api/datasets", tags=["Datasets"])


@router.post(
    "", response_model=APIResponse[DatasetResponse], status_code=status.HTTP_201_CREATED
)
def create_dataset(
    dataset_data: DatasetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(DATASET_OWNER, ADMINISTRATOR)),
) -> APIResponse[DatasetResponse]:
    """Create a dataset container owned by the authenticated user."""
    dataset = DatasetService.create_dataset(
        db=db,
        title=dataset_data.title,
        description=dataset_data.description,
        dataset_type=dataset_data.dataset_type,
        owner_id=current_user.id,
    )
    return success_response(
        DatasetResponse.model_validate(dataset), "Dataset created successfully."
    )


@router.get("", response_model=APIResponse[list[DatasetResponse]])
def get_datasets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[list[DatasetResponse]]:
    """Return datasets visible to the authenticated role."""
    datasets = DatasetService.get_datasets(db, current_user)
    return success_response(
        [DatasetResponse.model_validate(dataset) for dataset in datasets],
        f"{len(datasets)} dataset(s) returned.",
    )


@router.get("/{dataset_id}", response_model=APIResponse[DatasetResponse])
def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[DatasetResponse]:
    """Return one dataset when it exists and is visible to the caller."""
    dataset = DatasetService.get_dataset(db, dataset_id)
    if dataset is None:
        raise NotFoundError("Dataset not found.")
    if current_user.role != ADMINISTRATOR and dataset.owner_id not in (
        None,
        current_user.id,
    ):
        raise NotFoundError("Dataset not found.")
    return success_response(
        DatasetResponse.model_validate(dataset), "Dataset returned successfully."
    )


@router.put("/{dataset_id}", response_model=APIResponse[DatasetResponse])
def update_dataset(
    dataset_id: int,
    dataset_data: DatasetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(DATASET_OWNER, ADMINISTRATOR)),
) -> APIResponse[DatasetResponse]:
    """Update dataset metadata after checking ownership."""
    dataset = DatasetService.update_dataset(
        db=db,
        dataset_id=dataset_id,
        actor=current_user,
        title=dataset_data.title,
        description=dataset_data.description,
        dataset_type=dataset_data.dataset_type,
    )
    return success_response(
        DatasetResponse.model_validate(dataset), "Dataset updated successfully."
    )


@router.post(
    "/{dataset_id}/upload",
    response_model=APIResponse[DatasetUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload and parse a dataset file",
)
async def upload_dataset(
    dataset_id: int,
    file: UploadFile = File(...),
    text_column: str | None = Form(default=None),
    replace_existing: bool = Form(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(DATASET_OWNER, ADMINISTRATOR)),
) -> APIResponse[DatasetUploadResponse]:
    """Import CSV, JSON, JSONL or XLSX records into the dataset."""
    dataset = DatasetService.require_manage_access(db, dataset_id, current_user)
    count = await DatasetImportService.import_file(
        db=db,
        dataset=dataset,
        upload=file,
        text_column=text_column.strip() if text_column else None,
        replace_existing=replace_existing,
    )
    response = DatasetUploadResponse(
        dataset_id=dataset.id,
        filename=dataset.source_filename or file.filename or "dataset",
        format=dataset.source_format or "unknown",
        records_imported=count,
        total_records=dataset.record_count,
        replaced_existing=replace_existing,
    )
    return success_response(
        response, f"Imported {count:,} dataset record(s) successfully."
    )


@router.delete("/{dataset_id}", response_model=APIResponse[None])
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(DATASET_OWNER, ADMINISTRATOR)),
) -> APIResponse[None]:
    """Delete a dataset and its dependent workflow records."""
    DatasetService.delete_dataset(db, dataset_id, current_user)
    return success_response(None, "Dataset deleted successfully.")
