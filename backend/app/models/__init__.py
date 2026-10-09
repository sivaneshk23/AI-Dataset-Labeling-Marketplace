"""ORM model registry.

Importing this package registers every table on ``Base.metadata``, which is
what the test suite and the schema bootstrap rely on.
"""

from backend.app.models.annotation import Annotation
from backend.app.models.annotation_review import AnnotationReview
from backend.app.models.annotation_task import AnnotationTask
from backend.app.models.dataset import Dataset
from backend.app.models.dataset_record import DatasetRecord
from backend.app.models.job_assignment import JobAssignment
from backend.app.models.labeling_job import LabelingJob
from backend.app.models.review import Review
from backend.app.models.user import User

__all__ = [
    "Annotation",
    "AnnotationReview",
    "AnnotationTask",
    "Dataset",
    "DatasetRecord",
    "JobAssignment",
    "LabelingJob",
    "Review",
    "User",
]
