"""Unit tests for the progress tracking and platform analytics service.

These aggregates drive the dashboard tiles and the per-job progress view, so
the tests check the counters a dataset owner sees rather than only that the
call returns.
"""

import pytest

from backend.app.core.errors import NotFoundError
from backend.app.core.roles import ANNOTATOR
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.annotation_review_service import (
    AnnotationReviewService,
)
from backend.app.services.annotation_service import AnnotationService

ITEMS = (
    "Refund request for the damaged order.",
    "Delivery driver left the parcel at the front door.",
)


def _labelled(db_session, accounts, build_workflow):
    """Create a workflow with two submitted annotations."""
    workflow = build_workflow(items=ITEMS)

    for task in workflow["tasks"]:
        AnnotationService.submit_annotation(
            db_session,
            task.id,
            accounts["annotator"],
            "refund request",
            confidence=0.8,
        )

    workflow["annotations"] = [
        AnnotationService.get_annotations_for_task(db_session, task.id)[0]
        for task in workflow["tasks"]
    ]

    return workflow


class TestJobProgress:
    """Progress snapshot of a single labeling job."""

    def test_missing_jobs_are_reported(self, db_session):
        with pytest.raises(NotFoundError, match=r"Labeling job not found\."):
            AnalyticsService.job_progress(db_session, 999999)

    def test_progress_counts_tasks_and_reviews(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = _labelled(db_session, accounts, build_workflow)
        job_id = workflow["job"].id

        AnnotationReviewService.submit_review(
            db_session,
            workflow["annotations"][0].id,
            accounts["dataset_owner"],
            "approved",
        )

        progress = AnalyticsService.job_progress(db_session, job_id)

        assert progress["job_id"] == job_id
        assert progress["job_title"] == "Intent Classification Round 1"
        assert progress["dataset_id"] == workflow["dataset"].id
        assert progress["total_tasks"] == 2
        assert progress["total_annotations"] == 2
        assert progress["approved_tasks"] == 1
        assert progress["submitted_tasks"] == 1
        assert progress["open_tasks"] == 0
        assert progress["pending_reviews"] == 1
        assert progress["assigned_annotators"] == 1
        assert progress["ai_suggestions_used"] >= 0
        assert progress["average_confidence"] == 0.8
        assert 0 <= progress["completion_percentage"] <= 100

    def test_progress_handles_a_job_without_work(self, db_session, build_workflow):
        workflow = build_workflow(items=(), assign_to=None)

        progress = AnalyticsService.job_progress(db_session, workflow["job"].id)

        assert progress["total_tasks"] == 0
        assert progress["completion_percentage"] == 0.0
        assert progress["average_confidence"] is None
        assert progress["ai_agreement_rate"] is None
        assert progress["average_rating"] is None


class TestPlatformSummary:
    """Platform wide aggregates for the dashboard."""

    def test_summary_reports_an_empty_platform(self, db_session, accounts):
        summary = AnalyticsService.platform_summary(db_session)

        assert summary["total_users"] == 4
        assert summary["users_by_role"][ANNOTATOR] == 2
        assert summary["total_datasets"] == 0
        assert summary["total_jobs"] == 0
        assert summary["total_tasks"] == 0
        assert summary["total_annotations"] == 0
        assert summary["pending_reviews"] == 0
        assert summary["total_reviews"] == 0
        assert summary["annotation_completion_percentage"] == 0.0
        assert summary["ai_agreement_rate"] is None

    def test_summary_reflects_labelling_activity(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = _labelled(db_session, accounts, build_workflow)
        job_id = workflow["job"].id

        AnnotationReviewService.submit_review(
            db_session,
            workflow["annotations"][0].id,
            accounts["dataset_owner"],
            "approved",
        )

        summary = AnalyticsService.platform_summary(db_session)

        assert summary["total_datasets"] == 1
        assert summary["total_jobs"] == 1
        assert summary["active_jobs"] == 1
        assert summary["total_tasks"] == 2
        assert summary["tasks_by_status"]["approved"] == 1
        assert summary["total_annotations"] == 2
        assert summary["annotations_by_status"]["approved"] == 1
        assert summary["pending_reviews"] == 1
        assert summary["review_decisions"]["approved"] == 1
        assert summary["annotation_completion_percentage"] == 50.0
        assert summary["ai_suggestions_used"] >= 0

        assert AnalyticsService.job_progress(db_session, job_id)["job_id"] == job_id
