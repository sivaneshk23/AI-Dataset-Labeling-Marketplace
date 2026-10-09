"""Database access for imported dataset records."""

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.app.models.dataset_record import DatasetRecord


class DatasetRecordRepository:
    """Repository for source rows imported from dataset files."""

    @staticmethod
    def create_many(db: Session, records: list[DatasetRecord]) -> list[DatasetRecord]:
        """Persist a batch of dataset records in one transaction."""
        if not records:
            return []
        db.add_all(records)
        db.flush()
        return records

    @staticmethod
    def get_by_dataset(
        db: Session,
        dataset_id: int,
        offset: int = 0,
        limit: int = 1000,
    ) -> list[DatasetRecord]:
        """Return imported records in source-row order."""
        statement = (
            select(DatasetRecord)
            .where(DatasetRecord.dataset_id == dataset_id)
            .order_by(DatasetRecord.row_number.asc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.scalars(statement).all())

    @staticmethod
    def count_by_dataset(db: Session, dataset_id: int) -> int:
        """Return the number of imported source records."""
        from sqlalchemy import func

        return int(
            db.scalar(
                select(func.count(DatasetRecord.id)).where(
                    DatasetRecord.dataset_id == dataset_id
                )
            )
            or 0
        )

    @staticmethod
    def delete_by_dataset(db: Session, dataset_id: int) -> None:
        """Delete all source records belonging to a dataset."""
        db.execute(delete(DatasetRecord).where(DatasetRecord.dataset_id == dataset_id))
