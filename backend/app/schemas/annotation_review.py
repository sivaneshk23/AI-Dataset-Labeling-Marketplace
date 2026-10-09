"""Validation schemas for annotation quality reviews."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.models.annotation_review import REVIEW_DECISIONS


class AnnotationReviewCreate(BaseModel):
    """Payload used by a reviewer to record a quality decision."""

    annotation_id: int = Field(gt=0)
    decision: str
    comment: str | None = Field(
        default=None,
        max_length=2000,
    )

    @field_validator("decision")
    @classmethod
    def validate_decision(cls, value: str) -> str:
        """Ensure the decision is one of the supported values."""
        normalised = value.strip().lower().replace("-", "_")

        if normalised not in REVIEW_DECISIONS:
            raise ValueError(
                "Unsupported decision. Allowed values: "
                + ", ".join(REVIEW_DECISIONS)
                + "."
            )

        return normalised

    @field_validator("comment")
    @classmethod
    def clean_comment(cls, value: str | None) -> str | None:
        """Trim the review comment and convert blanks to None."""
        if value is None:
            return None

        cleaned = value.strip()

        return cleaned or None


class AnnotationReviewUpdate(BaseModel):
    """Payload used to correct a previously recorded decision."""

    decision: str | None = None
    comment: str | None = Field(
        default=None,
        max_length=2000,
    )

    @field_validator("decision")
    @classmethod
    def validate_decision(cls, value: str | None) -> str | None:
        """Ensure the decision is one of the supported values."""
        if value is None:
            return None

        normalised = value.strip().lower().replace("-", "_")

        if normalised not in REVIEW_DECISIONS:
            raise ValueError(
                "Unsupported decision. Allowed values: "
                + ", ".join(REVIEW_DECISIONS)
                + "."
            )

        return normalised


class AnnotationReviewResponse(BaseModel):
    """Quality review representation returned by the API."""

    id: int
    annotation_id: int
    reviewer_id: int
    decision: str
    comment: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
