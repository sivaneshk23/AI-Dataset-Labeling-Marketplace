"""Validation schemas for annotations."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.models.annotation import ANNOTATION_STATUSES


def _clean_label(value: str) -> str:
    """Validate and normalise a label value."""
    cleaned = " ".join(str(value).split())

    if not cleaned:
        raise ValueError("label must not be empty.")

    return cleaned


class AnnotationCreate(BaseModel):
    """Payload used by an annotator to submit a label."""

    task_id: int = Field(gt=0)
    label: str = Field(
        min_length=1,
        max_length=120,
    )
    notes: str | None = Field(
        default=None,
        max_length=2000,
    )
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Annotator confidence between 0 and 1.",
    )

    @field_validator("label")
    @classmethod
    def validate_label(cls, value: str) -> str:
        """Collapse whitespace and reject empty labels."""
        return _clean_label(value)

    @field_validator("notes")
    @classmethod
    def clean_notes(cls, value: str | None) -> str | None:
        """Trim notes and convert blank strings to None."""
        if value is None:
            return None

        cleaned = value.strip()

        return cleaned or None


class AnnotationUpdate(BaseModel):
    """Payload used to revise an existing annotation."""

    label: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
    )
    notes: str | None = Field(
        default=None,
        max_length=2000,
    )
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    @field_validator("label")
    @classmethod
    def validate_label(cls, value: str | None) -> str | None:
        """Collapse whitespace and reject empty labels."""
        if value is None:
            return None

        return _clean_label(value)


class AnnotationResponse(BaseModel):
    """Annotation representation returned by the API."""

    id: int
    task_id: int
    annotator_id: int
    label: str
    notes: str | None
    confidence: float | None
    ai_suggested_label: str | None
    ai_confidence: float | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class AnnotationStatusResponse(BaseModel):
    """Result of a status transition performed during review."""

    annotation_id: int
    task_id: int
    annotation_status: str
    task_status: str
    job_status: str


ANNOTATION_STATUS_OPTIONS = ANNOTATION_STATUSES
