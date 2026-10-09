from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DatasetBase(BaseModel):
    """Fields shared by dataset create/update requests."""

    title: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=10, max_length=5000)
    dataset_type: str = Field(min_length=2, max_length=50)


class DatasetCreate(DatasetBase):
    """Payload used to create a dataset."""


class DatasetResponse(DatasetBase):
    """Dataset metadata returned to the frontend."""

    id: int
    owner_id: int | None
    source_filename: str | None
    source_format: str | None
    source_size_bytes: int | None
    record_count: int
    uploaded_at: datetime | None

    @field_validator("record_count", mode="before")
    @classmethod
    def default_record_count(cls, value):
        """Treat legacy unsaved ORM instances as containing zero records."""
        return 0 if value is None else value

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetUploadResponse(BaseModel):
    """Outcome of a dataset-file import."""

    dataset_id: int
    filename: str
    format: str
    records_imported: int
    total_records: int
    replaced_existing: bool
