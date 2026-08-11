from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.dataset import Dataset


class DatasetRepository:

    @staticmethod
    def create(
        db: Session,
        dataset: Dataset,
    ) -> Dataset:
        db.add(dataset)
        db.commit()
        db.refresh(dataset)

        return dataset

    @staticmethod
    def get_by_id(
        db: Session,
        dataset_id: int,
    ) -> Dataset | None:
        statement = select(Dataset).where(
            Dataset.id == dataset_id
        )

        return db.scalar(statement)

    @staticmethod
    def get_all(
        db: Session,
    ) -> list[Dataset]:
        statement = select(Dataset).order_by(
            Dataset.id.desc()
        )

        return list(
            db.scalars(statement).all()
        )

    @staticmethod
    def update(
        db: Session,
        dataset: Dataset,
    ) -> Dataset:
        db.commit()
        db.refresh(dataset)

        return dataset

    @staticmethod
    def delete(
        db: Session,
        dataset: Dataset,
    ) -> None:
        db.delete(dataset)
        db.commit()