"""AI enhancement endpoints (Day 42-59).

Exposes AI pre-labelling, per-annotation quality reports and job level quality
insights. All routes are additive: the base marketplace keeps working when the
optional external AI provider is disabled.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.dependencies import (
    get_current_user,
    require_roles,
)
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.errors import PermissionDeniedError
from backend.app.core.roles import (
    ADMINISTRATOR,
    ANNOTATOR,
    DATASET_OWNER,
)
from backend.app.models.user import User
from backend.app.schemas.ai import (
    AIStatusResponse,
    JobInsightsResponse,
    LabelSuggestionRequest,
    LabelSuggestionResponse,
    QualityFlag,
    QualityReportResponse,
)
from backend.app.schemas.response import (
    APIResponse,
    success_response,
)
from backend.app.services.ai_service import AIService
from backend.app.services.annotation_service import (
    AnnotationService,
)
from backend.app.services.annotation_task_service import AnnotationTaskService

router = APIRouter(
    prefix="/api/ai",
    tags=["AI Enhancement"],
)


@router.get(
    "/status",
    response_model=APIResponse[AIStatusResponse],
    summary="Current AI provider configuration",
)
def get_ai_status(
    current_user: User = Depends(get_current_user),
) -> APIResponse[AIStatusResponse]:
    """Report which AI provider is active and whether it is external."""
    status_payload = AIStatusResponse(
        provider=AIService.provider_name(),
        model=(
            settings.gemini_model
            if AIService.uses_external_provider()
            else "local-similarity-knn"
        ),
        external_provider_enabled=AIService.uses_external_provider(),
        minimum_confidence=settings.ai_min_confidence,
    )

    return success_response(
        status_payload,
        "AI provider status returned successfully.",
    )


@router.post(
    "/jobs/{job_id}/suggest",
    response_model=APIResponse[LabelSuggestionResponse],
    summary="Suggest a label for a record inside a labeling job",
)
def suggest_label(
    job_id: int,
    payload: LabelSuggestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[LabelSuggestionResponse]:
    """Return an AI pre-labelling suggestion with a confidence score."""
    job = AIService._require_job(db, job_id)
    if current_user.role == ANNOTATOR:
        if payload.task_id is None:
            raise PermissionDeniedError(
                "Annotators must request AI assistance for an assigned task."
            )
        task = AnnotationTaskService.require_task(db, payload.task_id)
        if task.job_id != job_id or task.assigned_to != current_user.id:
            raise PermissionDeniedError(
                "You can only use AI assistance for your assigned task."
            )
    elif current_user.role != ADMINISTRATOR and job.created_by != current_user.id:
        raise PermissionDeniedError("You do not own this labeling job.")

    suggestion = AIService.suggest_label(
        db,
        job_id,
        payload.input_text,
        payload.candidate_labels,
    )

    message = (
        "AI label suggestion generated successfully."
        if suggestion.label
        else suggestion.rationale
    )

    return success_response(
        LabelSuggestionResponse(
            label=suggestion.label,
            confidence=suggestion.confidence,
            rationale=suggestion.rationale,
            provider=suggestion.provider,
            alternatives=[
                {"label": label, "confidence": confidence}
                for label, confidence in suggestion.alternatives
            ],
        ),
        message,
    )


@router.get(
    "/jobs/{job_id}/insights",
    response_model=APIResponse[JobInsightsResponse],
    summary="AI quality insights for a labeling job",
)
def get_job_insights(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[JobInsightsResponse]:
    """Return agreement, duplicate and quality metrics for a job."""
    insights = AIService.job_insights(db, job_id)

    return success_response(
        JobInsightsResponse.model_validate(insights),
        "AI quality insights generated successfully.",
    )


@router.get(
    "/annotations/{annotation_id}/quality",
    response_model=APIResponse[QualityReportResponse],
    summary="AI quality report for a submitted annotation",
)
def get_annotation_quality(
    annotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse[QualityReportResponse]:
    """Score a submitted annotation and explain the detected issues."""
    annotation = AnnotationService.require_annotation(
        db,
        annotation_id,
    )

    task = AnnotationTaskService.require_task(db, annotation.task_id)
    job = AIService._require_job(db, task.job_id)
    if current_user.role == ANNOTATOR and annotation.annotator_id != current_user.id:
        raise PermissionDeniedError("You can only inspect your own annotation quality.")
    if current_user.role == DATASET_OWNER and job.created_by != current_user.id:
        raise PermissionDeniedError("You do not own this labeling job.")

    report = AIService.evaluate_annotation(db, annotation)

    return success_response(
        QualityReportResponse(
            annotation_id=annotation.id,
            task_id=annotation.task_id,
            quality_score=report.score,
            recommendation=report.recommendation,
            provider=AIService.provider_name(),
            ai_agreement=report.agreement,
            flags=[
                QualityFlag(
                    code=issue.code,
                    message=issue.message,
                    severity=issue.severity,
                )
                for issue in report.issues
            ],
        ),
        "AI quality report generated successfully.",
    )
