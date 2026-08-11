from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.dataset import Dataset


class DatasetRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, dataset: Dataset) -> Dataset:
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        return dataset

    def get_by_id(self, dataset_id: int) -> Dataset | None:
        statement = select(Dataset).where(Dataset.id == dataset_id)
        return self.db.scalar(statement)

    def get_all(self) -> list[Dataset]:
        statement = select(Dataset).order_by(Dataset.id)
        return list(self.db.scalars(statement).all())

    def update(self, dataset: Dataset) -> Dataset:
        self.db.commit()
        self.db.refresh(dataset)
        return dataset

    def delete(self, dataset: Dataset) -> None:
        self.db.delete(dataset)
        self.db.commit()