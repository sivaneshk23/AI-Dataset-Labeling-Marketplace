from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.dataset import DatasetCreate, DatasetResponse
from backend.app.schemas.response import APIResponse
from backend.app.services.dataset_service import DatasetService


router = APIRouter(
    prefix="/api/datasets",
    tags=["Datasets"],
)


@router.post(
    "",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_dataset(
    dataset_data: DatasetCreate,
    db: Session = Depends(get_db),
):
    service = DatasetService(db)
    dataset = service.create_dataset(dataset_data)

    return APIResponse(
        success=True,
        data=DatasetResponse.model_validate(dataset),
        message="Dataset created successfully",
    )


@router.get(
    "",
    response_model=APIResponse,
)
def get_datasets(
    db: Session = Depends(get_db),
):
    service = DatasetService(db)
    datasets = service.get_datasets()

    return APIResponse(
        success=True,
        data=[
            DatasetResponse.model_validate(dataset)
            for dataset in datasets
        ],
        message="Datasets retrieved successfully",
    )


@router.get(
    "/{dataset_id}",
    response_model=APIResponse,
)
def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
):
    service = DatasetService(db)
    dataset = service.get_dataset(dataset_id)

    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found",
        )

    return APIResponse(
        success=True,
        data=DatasetResponse.model_validate(dataset),
        message="Dataset retrieved successfully",
    )


@router.put(
    "/{dataset_id}",
    response_model=APIResponse,
)
def update_dataset(
    dataset_id: int,
    dataset_data: DatasetCreate,
    db: Session = Depends(get_db),
):
    service = DatasetService(db)
    dataset = service.update_dataset(dataset_id, dataset_data)

    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found",
        )

    return APIResponse(
        success=True,
        data=DatasetResponse.model_validate(dataset),
        message="Dataset updated successfully",
    )


@router.delete(
    "/{dataset_id}",
    response_model=APIResponse,
)
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
):
    service = DatasetService(db)
    deleted = service.delete_dataset(dataset_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found",
        )

    return APIResponse(
        success=True,
        data=None,
        message="Dataset deleted successfully",
    )