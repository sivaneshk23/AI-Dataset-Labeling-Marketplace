"""Demo data seeding script.

Creates one administrator, one dataset owner, two annotators, a dataset, a
labeling job, annotation tasks, a few annotations and a quality review so the
application can be demonstrated immediately after deployment.

Usage::

    python -m backend.seed_demo_data

The script is idempotent: re-running it only adds the missing records.
"""

from sqlalchemy.orm import Session

from backend.app.core.database import Base, SessionLocal, engine
from backend.app.core.logging import configure_logging, get_logger
from backend.app.core.roles import (
    ADMINISTRATOR,
    ANNOTATOR,
    DATASET_OWNER,
)
from backend.app.models.annotation import Annotation  # noqa: F401
from backend.app.models.annotation_review import (  # noqa: F401
    AnnotationReview,
)
from backend.app.models.annotation_task import (  # noqa: F401
    AnnotationTask,
)
from backend.app.models.dataset import Dataset  # noqa: F401
from backend.app.models.job_assignment import (  # noqa: F401
    JobAssignment,
)
from backend.app.models.labeling_job import LabelingJob  # noqa: F401
from backend.app.models.review import Review  # noqa: F401
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate
from backend.app.services.annotation_review_service import (
    AnnotationReviewService,
)
from backend.app.services.annotation_service import AnnotationService
from backend.app.services.annotation_task_service import (
    AnnotationTaskService,
)
from backend.app.services.dataset_service import DatasetService
from backend.app.services.labeling_job_service import (
    LabelingJobService,
)
from backend.app.services.user_service import UserService

configure_logging()

logger = get_logger(__name__)

DEMO_PASSWORD = "Capstone@2026"

DEMO_USERS = (
    ("Platform Administrator", "admin@marketplace.dev", ADMINISTRATOR),
    ("Dataset Owner", "owner@marketplace.dev", DATASET_OWNER),
    ("Annotator One", "annotator1@marketplace.dev", ANNOTATOR),
    ("Annotator Two", "annotator2@marketplace.dev", ANNOTATOR),
)

DEMO_RECORDS = (
    "Delivery driver left the parcel at the front door.",
    "The invoice total does not match the purchase order.",
    "Customer asked for a refund because the item arrived damaged.",
    "Support agent resolved the password reset request.",
    "The shipment is delayed due to heavy rain in the region.",
    "Duplicate charge appears twice on the monthly statement.",
)

DEMO_LABELS = (
    "delivery",
    "billing",
    "refund",
    "account",
    "delivery",
    "billing",
)


def ensure_users(db: Session) -> dict[str, User]:
    """Create the demo accounts when they are missing."""
    users: dict[str, User] = {}
    existing = UserService.get_users(db)

    for name, email, role in DEMO_USERS:
        match = next(
            (user for user in existing if user.email == email),
            None,
        )

        if match is None:
            match = UserService.create_user(
                db,
                UserCreate(
                    name=name,
                    email=email,
                    password=DEMO_PASSWORD,
                    role=(DATASET_OWNER if role == ADMINISTRATOR else role),
                ),
                role=role,
                allow_privileged=True,
            )

            logger.info("Created demo user %s (%s).", email, role)

        users[role] = match

    return users


def seed() -> None:
    """Create the demo dataset, job, tasks, annotations and review."""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        users = ensure_users(db)

        dataset = next(
            (
                item
                for item in DatasetService.get_datasets(db)
                if item.title == "Customer Support Tickets"
            ),
            None,
        )

        if dataset is None:
            dataset = DatasetService.create_dataset(
                db,
                title="Customer Support Tickets",
                description=(
                    "Support conversations labelled by intent for a ticket "
                    "routing classifier."
                ),
                dataset_type="Natural Language Processing",
            )

            logger.info("Created demo dataset %s.", dataset.title)

        job = next(
            (
                item
                for item in LabelingJobService.get_jobs(db)
                if item.title == "Intent Classification Round 1"
            ),
            None,
        )

        if job is None:
            job = LabelingJobService.create_job(
                db=db,
                dataset_id=dataset.id,
                created_by=users[DATASET_OWNER].id,
                title="Intent Classification Round 1",
                description=(
                    "Label each support ticket with its primary customer intent."
                ),
                status="open",
            )

            logger.info("Created demo labeling job %s.", job.title)

        if not AnnotationTaskService.get_tasks_for_job(db, job.id):
            AnnotationTaskService.create_tasks_bulk(
                db=db,
                job_id=job.id,
                items=list(DEMO_RECORDS),
                assigned_to=users[ANNOTATOR].id,
            )

            logger.info("Created demo annotation tasks.")

        tasks = AnnotationTaskService.get_tasks_for_job(db, job.id)

        for task, label in zip(tasks, DEMO_LABELS, strict=False):
            if AnnotationService.get_annotations_for_task(db, task.id):
                continue

            annotation = AnnotationService.submit_annotation(
                db=db,
                task_id=task.id,
                annotator=users[ANNOTATOR],
                label=label,
                notes="Labelled during demo seeding.",
                confidence=0.9,
            )

            if label in {"delivery", "billing"}:
                AnnotationReviewService.submit_review(
                    db=db,
                    annotation_id=annotation.id,
                    reviewer=users[DATASET_OWNER],
                    decision="approved",
                    comment="Verified against the labelling guidelines.",
                )

        logger.info(
            "Demo data ready. Sign in with owner@marketplace.dev / %s",
            DEMO_PASSWORD,
        )
    finally:
        db.close()


if __name__ == "__main__":
    seed()
