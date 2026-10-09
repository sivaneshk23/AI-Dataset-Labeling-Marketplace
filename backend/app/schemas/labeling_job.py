from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LabelingJobBase(BaseModel):
    """Fields shared by labeling-job requests."""

    title: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=10, max_length=5000)
    status: str = Field(default="open", max_length=30)
    annotation_type: str = Field(default="single_label_text", max_length=40)
    label_options: list[str] = Field(default_factory=list, max_length=30)

    @field_validator("label_options")
    @classmethod
    def clean_labels(cls, values: list[str]) -> list[str]:
        """Normalize and deduplicate the configured label vocabulary."""
        cleaned: list[str] = []
        seen: set[str] = set()
        for value in values:
            label = " ".join(str(value).split()).strip()
            if not label:
                continue
            key = label.casefold()
            if key not in seen:
                seen.add(key)
                cleaned.append(label[:120])
        if len(cleaned) > 30:
            raise ValueError("A labeling job can contain at most 30 labels.")
        return cleaned


class LabelingJobCreate(LabelingJobBase):
    """Payload used to create a labeling job."""

    dataset_id: int = Field(gt=0)


class LabelingJobUpdate(BaseModel):
    """Payload used to update a labeling job."""

    title: str | None = Field(default=None, min_length=3, max_length=150)
    description: str | None = Field(default=None, min_length=10, max_length=5000)
    status: str | None = Field(default=None, max_length=30)
    annotation_type: str | None = Field(default=None, max_length=40)
    label_options: list[str] | None = Field(default=None, max_length=30)


class LabelingJobResponse(LabelingJobBase):
    """Labeling job representation returned by the API."""

    id: int
    dataset_id: int
    created_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
