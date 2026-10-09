"""Shared pytest fixtures for the AI Dataset Labeling Marketplace test suite.

Two styles of tests are supported:

* service level unit tests that patch the repository layer (no database), and
* API/workflow tests that run against an in-memory SQLite database through
  ``fastapi.testclient.TestClient`` so the full stack (router -> service ->
  repository -> ORM) is exercised in CI without a PostgreSQL server.
"""

import os

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("ENVIRONMENT", "ci")
os.environ.setdefault(
    "SECRET_KEY", "ci-test-secret-key-please-do-not-use-in-production-123456"
)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import backend.app.models  # noqa: F401  (registers every table)
from backend.app.core.config import settings
from backend.app.core.database import Base, get_db
from backend.app.core.roles import (
    ADMINISTRATOR,
    ANNOTATOR,
    DATASET_OWNER,
)
from backend.app.core.security import create_access_token
from backend.app.main import app
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate
from backend.app.services.user_service import UserService

TEST_PASSWORD = "Password123"

# The rate limiter protects the public deployment: leaving it switched on would
# throttle this suite itself. tests/test_middleware.py re-enables it explicitly
# so the "429 Too Many Requests" path still has real coverage.
settings.rate_limit_enabled = False

DEMO_ACCOUNTS = {
    ADMINISTRATOR: ("Admin User", "admin@marketplace.dev"),
    DATASET_OWNER: ("Owner User", "owner@marketplace.dev"),
    ANNOTATOR: ("Annotator User", "annotator@marketplace.dev"),
    "second_annotator": ("Second Annotator", "annotator2@marketplace.dev"),
}


@pytest.fixture()
def db_session():
    """Provide a transactional in-memory SQLite session."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    testing_session = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    session = testing_session()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    """Provide a TestClient bound to the in-memory database."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def build_user(
    db_session,
    role: str,
    name: str,
    email: str,
) -> User:
    """Create a user with a specific role for API tests."""
    return UserService.create_user(
        db_session,
        UserCreate(
            name=name,
            email=email,
            password=TEST_PASSWORD,
            role=(DATASET_OWNER if role == ADMINISTRATOR else role),
        ),
        role=role,
        allow_privileged=True,
    )


def bearer_headers(user: User) -> dict[str, str]:
    """Build an authorization header for a user."""
    token = create_access_token(
        user_id=user.id,
        email=user.email,
    )

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def accounts(db_session) -> dict[str, User]:
    """Create one account per platform role."""
    created: dict[str, User] = {}

    for key, (name, email) in DEMO_ACCOUNTS.items():
        role = ANNOTATOR if key == "second_annotator" else key

        created[key] = build_user(
            db_session,
            role,
            name,
            email,
        )

    return created


@pytest.fixture()
def auth(accounts) -> dict[str, dict[str, str]]:
    """Provide ready-to-use authorization headers per role."""
    return {key: bearer_headers(user) for key, user in accounts.items()}


DEFAULT_TASK_ITEMS = (
    "Delivery driver left the parcel at the front door.",
    "The invoice total does not match the purchase order.",
    "Customer asked for a refund for a damaged item.",
)


@pytest.fixture()
def build_workflow(db_session, accounts):
    """Return a factory that creates a dataset, job and annotation tasks.

    The factory keeps the service level tests short while still exercising the
    real persistence layer.
    """
    from backend.app.services.annotation_task_service import (
        AnnotationTaskService,
    )
    from backend.app.services.dataset_service import (
        DatasetService,
    )
    from backend.app.services.labeling_job_service import (
        LabelingJobService,
    )

    def factory(
        items: tuple[str, ...] = DEFAULT_TASK_ITEMS,
        assign_to: str | None = "annotator",
        job_status: str = "open",
    ) -> dict:
        dataset = DatasetService.create_dataset(
            db_session,
            title="Customer Support Tickets",
            description="Support conversations labelled by intent.",
            dataset_type="Natural Language Processing",
        )

        job = LabelingJobService.create_job(
            db=db_session,
            dataset_id=dataset.id,
            created_by=accounts["dataset_owner"].id,
            title="Intent Classification Round 1",
            description="Label each ticket with its primary intent.",
            status=job_status,
        )

        tasks = [
            AnnotationTaskService.create_task(
                db_session,
                job.id,
                item,
                assigned_to=(accounts[assign_to].id if assign_to is not None else None),
            )
            for item in items
        ]

        return {
            "dataset": dataset,
            "job": job,
            "tasks": tasks,
        }

    return factory
