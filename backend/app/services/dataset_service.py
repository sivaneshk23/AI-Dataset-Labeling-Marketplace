"""Dataset business rules, ownership checks and upload lifecycle."""

from sqlalchemy.orm import Session

from backend.app.core.errors import NotFoundError, PermissionDeniedError
from backend.app.core.roles import ADMINISTRATOR
from backend.app.models.dataset import Dataset
from backend.app.models.user import User
from backend.app.repositories.dataset_repository import DatasetRepository


class DatasetService:
    """Manage datasets while enforcing owner-level isolation."""

    @staticmethod
    def create_dataset(
        db: Session,
        title: str,
        description: str,
        dataset_type: str,
        owner_id: int | None = None,
    ) -> Dataset:
        """Create a dataset and associate it with its owner."""
        dataset = Dataset(
            title=title.strip(),
            description=description.strip(),
            dataset_type=dataset_type.strip(),
            owner_id=owner_id,
        )
        return DatasetRepository.create(db, dataset)

    @staticmethod
    def require_manage_access(db: Session, dataset_id: int, actor: User) -> Dataset:
        """Return a dataset when the caller may manage it."""
        dataset = DatasetRepository.get_by_id(db, dataset_id)
        if dataset is None:
            raise NotFoundError("Dataset not found.")
        if actor.role != ADMINISTRATOR and dataset.owner_id not in (None, actor.id):
            raise PermissionDeniedError("You do not own this dataset.")
        return dataset

    @staticmethod
    def get_dataset(db: Session, dataset_id: int) -> Dataset | None:
        """Return a dataset by identifier."""
        return DatasetRepository.get_by_id(db, dataset_id)

    @staticmethod
    def get_datasets(db: Session, actor: User | None = None) -> list[Dataset]:
        """Return datasets visible to the current role."""
        if actor is None or actor.role == ADMINISTRATOR:
            return DatasetRepository.get_all(db)
        return DatasetRepository.get_by_owner(db, actor.id)

    @staticmethod
    def update_dataset(
        db: Session,
        dataset_id: int,
        actor: User | None = None,
        title: str | None = None,
        description: str | None = None,
        dataset_type: str | None = None,
    ) -> Dataset:
        """Update dataset metadata after an ownership check."""
        dataset = DatasetRepository.get_by_id(db, dataset_id)
        if dataset is None:
            raise ValueError("Dataset not found.")
        if (
            actor is not None
            and actor.role != ADMINISTRATOR
            and dataset.owner_id not in (None, actor.id)
        ):
            raise PermissionDeniedError("You do not own this dataset.")
        if title is not None:
            dataset.title = title.strip()
        if description is not None:
            dataset.description = description.strip()
        if dataset_type is not None:
            dataset.dataset_type = dataset_type.strip()
        return DatasetRepository.update(db, dataset)

    @staticmethod
    def delete_dataset(db: Session, dataset_id: int, actor: User | None = None) -> None:
        """Delete a dataset after an ownership check."""
        dataset = DatasetRepository.get_by_id(db, dataset_id)
        if dataset is None:
            raise ValueError("Dataset not found.")
        if (
            actor is not None
            and actor.role != ADMINISTRATOR
            and dataset.owner_id not in (None, actor.id)
        ):
            raise PermissionDeniedError("You do not own this dataset.")
        DatasetRepository.delete(db, dataset)
