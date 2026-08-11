from sqlalchemy.orm import Session

from backend.app.models.dataset import Dataset
from backend.app.repositories.dataset_repository import (
    DatasetRepository,
)


class DatasetService:

    @staticmethod
    def create_dataset(
        db: Session,
        title: str,
        description: str,
        dataset_type: str,
    ) -> Dataset:

        dataset = Dataset(
            title=title,
            description=description,
            dataset_type=dataset_type,
        )

        return DatasetRepository.create(
            db,
            dataset,
        )

    @staticmethod
    def get_dataset(
        db: Session,
        dataset_id: int,
    ) -> Dataset | None:

        return DatasetRepository.get_by_id(
            db,
            dataset_id,
        )

    @staticmethod
    def get_datasets(
        db: Session,
    ) -> list[Dataset]:

        return DatasetRepository.get_all(
            db,
        )

    @staticmethod
    def update_dataset(
        db: Session,
        dataset_id: int,
        title: str | None = None,
        description: str | None = None,
        dataset_type: str | None = None,
    ) -> Dataset:

        dataset = DatasetRepository.get_by_id(
            db,
            dataset_id,
        )

        if dataset is None:
            raise ValueError(
                "Dataset not found."
            )

        if title is not None:
            dataset.title = title

        if description is not None:
            dataset.description = description

        if dataset_type is not None:
            dataset.dataset_type = dataset_type

        return DatasetRepository.update(
            db,
            dataset,
        )

    @staticmethod
    def delete_dataset(
        db: Session,
        dataset_id: int,
    ) -> None:

        dataset = DatasetRepository.get_by_id(
            db,
            dataset_id,
        )

        if dataset is None:
            raise ValueError(
                "Dataset not found."
            )

        DatasetRepository.delete(
            db,
            dataset,
        )