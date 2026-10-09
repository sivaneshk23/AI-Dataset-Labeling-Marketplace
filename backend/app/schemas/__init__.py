"""Pydantic schema registry."""

from backend.app.schemas.ai import (
    AIStatusResponse,
    AnnotatorStat,
    FlaggedAnnotation,
    JobInsightsResponse,
    LabelAlternative,
    LabelCount,
    LabelSuggestionRequest,
    LabelSuggestionResponse,
    QualityFlag,
    QualityReportResponse,
)
from backend.app.schemas.analytics import (
    JobProgressResponse,
    PlatformSummaryResponse,
)
from backend.app.schemas.annotation import (
    AnnotationCreate,
    AnnotationResponse,
    AnnotationStatusResponse,
    AnnotationUpdate,
)
from backend.app.schemas.annotation_review import (
    AnnotationReviewCreate,
    AnnotationReviewResponse,
    AnnotationReviewUpdate,
)
from backend.app.schemas.annotation_task import (
    AnnotationTaskAssign,
    AnnotationTaskBase,
    AnnotationTaskBulkCreate,
    AnnotationTaskCreate,
    AnnotationTaskResponse,
    AnnotationTaskUpdate,
)
from backend.app.schemas.auth import (
    LoginRequest,
    TokenResponse,
)
from backend.app.schemas.dataset import (
    DatasetBase,
    DatasetCreate,
    DatasetResponse,
)
from backend.app.schemas.job_assignment import (
    JobAssignmentBase,
    JobAssignmentCreate,
    JobAssignmentResponse,
    JobAssignmentUpdate,
)
from backend.app.schemas.labeling_job import (
    LabelingJobBase,
    LabelingJobCreate,
    LabelingJobResponse,
    LabelingJobUpdate,
)
from backend.app.schemas.response import (
    APIResponse,
    error_response,
    success_response,
)
from backend.app.schemas.review import (
    ReviewCreate,
    ReviewResponse,
    ReviewUpdate,
)
from backend.app.schemas.user import (
    UserBase,
    UserCreate,
    UserResponse,
    UserRoleUpdate,
    UserStatusUpdate,
)

__all__ = [
    "AIStatusResponse",
    "APIResponse",
    "AnnotationCreate",
    "AnnotationResponse",
    "AnnotationReviewCreate",
    "AnnotationReviewResponse",
    "AnnotationReviewUpdate",
    "AnnotationStatusResponse",
    "AnnotationTaskAssign",
    "AnnotationTaskBase",
    "AnnotationTaskBulkCreate",
    "AnnotationTaskCreate",
    "AnnotationTaskResponse",
    "AnnotationTaskUpdate",
    "AnnotationUpdate",
    "AnnotatorStat",
    "DatasetBase",
    "DatasetCreate",
    "DatasetResponse",
    "FlaggedAnnotation",
    "JobAssignmentBase",
    "JobAssignmentCreate",
    "JobAssignmentResponse",
    "JobAssignmentUpdate",
    "JobInsightsResponse",
    "JobProgressResponse",
    "LabelAlternative",
    "LabelCount",
    "LabelSuggestionRequest",
    "LabelSuggestionResponse",
    "LabelingJobBase",
    "LabelingJobCreate",
    "LabelingJobResponse",
    "LabelingJobUpdate",
    "LoginRequest",
    "PlatformSummaryResponse",
    "QualityFlag",
    "QualityReportResponse",
    "ReviewCreate",
    "ReviewResponse",
    "ReviewUpdate",
    "TokenResponse",
    "UserBase",
    "UserCreate",
    "UserResponse",
    "UserRoleUpdate",
    "UserStatusUpdate",
    "error_response",
    "success_response",
]
