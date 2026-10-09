from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from backend.app.models.dataset import Dataset


class DatasetRepository:
    """Database access for datasets."""

    @staticmethod
    def create(db: Session, dataset: Dataset) -> Dataset:
        """Persist and return a dataset."""
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        return dataset

    @staticmethod
    def get_by_id(db: Session, dataset_id: int) -> Dataset | None:
        """Return a dataset by identifier."""
        return db.get(Dataset, dataset_id)

    @staticmethod
    def get_all(db: Session) -> list[Dataset]:
        """Return all datasets ordered newest first."""
        return list(
            db.scalars(select(Dataset).order_by(Dataset.created_at.desc())).all()
        )

    @staticmethod
    def get_by_owner(db: Session, owner_id: int) -> list[Dataset]:
        """Return datasets owned by a user, including legacy unowned records."""
        return list(
            db.scalars(
                select(Dataset)
                .where(or_(Dataset.owner_id == owner_id, Dataset.owner_id.is_(None)))
                .order_by(Dataset.created_at.desc())
            ).all()
        )

    @staticmethod
    def update(db: Session, dataset: Dataset) -> Dataset:
        """Persist changes to a dataset."""
        db.commit()
        db.refresh(dataset)
        return dataset

    @staticmethod
    def delete(db: Session, dataset: Dataset) -> None:
        """Delete a dataset."""
        db.delete(dataset)
        db.commit()
