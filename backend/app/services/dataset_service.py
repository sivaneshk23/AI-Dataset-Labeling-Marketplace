from sqlalchemy.orm import Session

from backend.app.models.dataset import Dataset
from backend.app.repositories.dataset_repository import DatasetRepository
from backend.app.schemas.dataset import DatasetCreate


class DatasetService:
    def __init__(self, db: Session):
        self.repository = DatasetRepository(db)

    def create_dataset(self, dataset_data: DatasetCreate) -> Dataset:
        dataset = Dataset(
            title=dataset_data.title,
            description=dataset_data.description,
            dataset_type=dataset_data.dataset_type,
        )

        return self.repository.create(dataset)

    def get_dataset(self, dataset_id: int) -> Dataset | None:
        return self.repository.get_by_id(dataset_id)

    def get_datasets(self) -> list[Dataset]:
        return self.repository.get_all()

    def update_dataset(
        self,
        dataset_id: int,
        dataset_data: DatasetCreate,
    ) -> Dataset | None:
        dataset = self.repository.get_by_id(dataset_id)

        if dataset is None:
            return None

        dataset.title = dataset_data.title
        dataset.description = dataset_data.description
        dataset.dataset_type = dataset_data.dataset_type

        return self.repository.update(dataset)

    def delete_dataset(self, dataset_id: int) -> bool:
        dataset = self.repository.get_by_id(dataset_id)

        if dataset is None:
            return False

        self.repository.delete(dataset)
        return True