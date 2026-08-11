from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_current_user
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.dataset import (
    DatasetCreate,
    DatasetResponse,
)
from backend.app.services.dataset_service import DatasetService


router = APIRouter(
    prefix="/api/datasets",
    tags=["Datasets"],
)


@router.post(
    "",
    response_model=DatasetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_dataset(
    dataset_data: DatasetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DatasetService.create_dataset(
        db=db,
        title=dataset_data.title,
        description=dataset_data.description,
        dataset_type=dataset_data.dataset_type,
    )


@router.get(
    "",
    response_model=list[DatasetResponse],
)
def get_datasets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DatasetService.get_datasets(db)


@router.get(
    "/{dataset_id}",
    response_model=DatasetResponse,
)
def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = DatasetService.get_dataset(
        db,
        dataset_id,
    )

    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found.",
        )

    return dataset


@router.put(
    "/{dataset_id}",
    response_model=DatasetResponse,
)
def update_dataset(
    dataset_id: int,
    dataset_data: DatasetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return DatasetService.update_dataset(
            db=db,
            dataset_id=dataset_id,
            title=dataset_data.title,
            description=dataset_data.description,
            dataset_type=dataset_data.dataset_type,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.delete(
    "/{dataset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        DatasetService.delete_dataset(
            db,
            dataset_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return None