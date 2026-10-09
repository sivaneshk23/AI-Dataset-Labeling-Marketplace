"""Validation schemas for annotation tasks."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.models.annotation_task import TASK_STATUSES


class AnnotationTaskBase(BaseModel):
    """Fields shared by annotation task payloads."""

    input_text: str = Field(
        min_length=1,
        max_length=5000,
        description="Record, sentence or image reference to annotate.",
    )

    @field_validator("input_text")
    @classmethod
    def strip_input_text(cls, value: str) -> str:
        """Remove surrounding whitespace from the task payload."""
        cleaned = value.strip()

        if not cleaned:
            raise ValueError("input_text must not be empty.")

        return cleaned


class AnnotationTaskCreate(AnnotationTaskBase):
    """Payload used to create a single annotation task."""

    job_id: int = Field(gt=0)
    assigned_to: int | None = Field(
        default=None,
        gt=0,
    )


class AnnotationTaskBulkCreate(BaseModel):
    """Payload used to create several annotation tasks at once."""

    job_id: int = Field(gt=0)
    assigned_to: int | None = Field(
        default=None,
        gt=0,
    )
    items: list[str] = Field(
        min_length=1,
        max_length=500,
        description="List of records to convert into tasks.",
    )
    skip_duplicates: bool = True


class DatasetImportRequest(BaseModel):
    """Request to turn uploaded dataset records into annotation tasks."""

    dataset_id: int = Field(gt=0)
    job_id: int = Field(gt=0)
    assigned_to: int | None = Field(default=None, gt=0)
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=1000, ge=1, le=1000)
    skip_duplicates: bool = True


class AnnotationTaskAssign(BaseModel):
    """Payload used to assign a task to an annotator."""

    assigned_to: int = Field(gt=0)


class AnnotationTaskUpdate(BaseModel):
    """Payload used to update a task."""

    input_text: str | None = Field(
        default=None,
        min_length=1,
        max_length=5000,
    )
    status: str | None = None
    assigned_to: int | None = Field(
        default=None,
        gt=0,
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        """Ensure the requested task status is supported."""
        if value is None:
            return None

        normalised = value.strip().lower()

        if normalised not in TASK_STATUSES:
            raise ValueError(
                "Unsupported task status. Allowed values: "
                + ", ".join(TASK_STATUSES)
                + "."
            )

        return normalised


class AnnotationTaskResponse(AnnotationTaskBase):
    """Annotation task representation returned by the API."""

    id: int
    job_id: int
    dataset_record_id: int | None
    assigned_to: int | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
