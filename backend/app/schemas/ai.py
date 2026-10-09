"""Validation schemas for AI assisted annotation and quality control."""

from pydantic import BaseModel, Field, field_validator


class LabelSuggestionRequest(BaseModel):
    """Payload requesting an AI label suggestion for one record."""

    task_id: int | None = Field(default=None, gt=0)
    input_text: str = Field(
        min_length=1,
        max_length=5000,
    )
    candidate_labels: list[str] = Field(
        default_factory=list,
        max_length=50,
        description=(
            "Optional label set defined by the dataset owner. Labels already "
            "used in the job are always considered."
        ),
    )

    @field_validator("input_text")
    @classmethod
    def strip_input_text(cls, value: str) -> str:
        """Reject blank records."""
        cleaned = value.strip()

        if not cleaned:
            raise ValueError("input_text must not be empty.")

        return cleaned


class LabelAlternative(BaseModel):
    """Alternative label proposed by the AI provider."""

    label: str
    confidence: float = Field(ge=0.0, le=1.0)


class LabelSuggestionResponse(BaseModel):
    """AI generated label suggestion."""

    label: str
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
    provider: str
    alternatives: list[LabelAlternative] = Field(
        default_factory=list,
    )


class QualityFlag(BaseModel):
    """Single quality issue detected for an annotation."""

    code: str
    message: str
    severity: str


class QualityReportResponse(BaseModel):
    """AI quality report for a submitted annotation."""

    annotation_id: int
    task_id: int
    quality_score: float = Field(ge=0, le=100)
    recommendation: str
    provider: str
    ai_agreement: bool | None = None
    flags: list[QualityFlag] = Field(
        default_factory=list,
    )


class LabelCount(BaseModel):
    """Label frequency entry."""

    label: str
    count: int = Field(ge=0)
    share: float = Field(ge=0, le=100)


class FlaggedAnnotation(BaseModel):
    """Annotation highlighted by the AI quality engine."""

    annotation_id: int
    task_id: int
    label: str
    quality_score: float = Field(ge=0, le=100)
    flags: list[str] = Field(default_factory=list)


class AnnotatorStat(BaseModel):
    """Per-annotator productivity and agreement statistics."""

    annotator_id: int
    annotator_name: str
    annotations: int = Field(ge=0)
    approved: int = Field(ge=0)
    agreement_rate: float | None = None


class JobInsightsResponse(BaseModel):
    """AI generated quality insights for one labeling job."""

    job_id: int
    provider: str
    total_annotations: int = Field(ge=0)
    labelled_tasks: int = Field(ge=0)
    unlabelled_tasks: int = Field(ge=0)
    label_distribution: list[LabelCount] = Field(
        default_factory=list,
    )
    agreement_rate: float | None = None
    average_confidence: float | None = None
    ai_coverage: float = Field(ge=0, le=100)
    duplicate_annotations: int = Field(ge=0)
    flagged_annotations: list[FlaggedAnnotation] = Field(
        default_factory=list,
    )
    annotator_stats: list[AnnotatorStat] = Field(
        default_factory=list,
    )
    recommendations: list[str] = Field(
        default_factory=list,
    )


class AIStatusResponse(BaseModel):
    """Current AI provider configuration."""

    provider: str
    model: str
    external_provider_enabled: bool
    minimum_confidence: float = Field(ge=0.0, le=1.0)
