"""Unit tests for annotation quality review decisions.

Every decision must propagate to the annotation, to the task state machine and,
once every task is approved, to the parent labeling job.
"""

import pytest

from backend.app.core.errors import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
)
from backend.app.services.annotation_review_service import (
    AnnotationReviewService,
)
from backend.app.services.annotation_service import AnnotationService

ITEM = "Refund request for the damaged order."


def _submit(db_session, accounts, build_workflow, items=(ITEM,)):
    """Submit one annotation for every task in a fresh workflow."""
    workflow = build_workflow(items=items)
    annotations = [
        AnnotationService.submit_annotation(
            db_session,
            task.id,
            accounts["annotator"],
            "refund request",
        )
        for task in workflow["tasks"]
    ]

    return workflow, annotations


class TestReviewDecisions:
    """Decision handling and workflow propagation."""

    def test_approval_closes_a_finished_job(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow, annotations = _submit(db_session, accounts, build_workflow)

        review = AnnotationReviewService.submit_review(
            db_session,
            annotations[0].id,
            accounts["dataset_owner"],
            "approved",
            comment="label matches the guideline",
        )

        assert review.id is not None
        assert review.decision == "approved"
        assert review.comment == "label matches the guideline"
        assert annotations[0].status == "approved"
        assert workflow["tasks"][0].status == "approved"
        assert workflow["job"].status == "completed"

    def test_rejection_reopens_the_task(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow, annotations = _submit(db_session, accounts, build_workflow)

        review = AnnotationReviewService.submit_review(
            db_session,
            annotations[0].id,
            accounts["administrator"],
            "rejected",
        )

        assert review.decision == "rejected"
        assert review.comment is None
        assert annotations[0].status == "rejected"
        assert workflow["tasks"][0].status == "rejected"
        assert workflow["job"].status != "completed"

    def test_revision_request_moves_the_task_back_to_progress(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow, annotations = _submit(db_session, accounts, build_workflow)

        AnnotationReviewService.submit_review(
            db_session,
            annotations[0].id,
            accounts["dataset_owner"],
            "needs_revision",
            comment="Use the shorter label from the guideline.",
        )

        assert annotations[0].status == "needs_revision"
        assert workflow["tasks"][0].status == "in_progress"


class TestReviewGuardRails:
    """Situations that must never produce a review decision."""

    def test_reviewers_cannot_review_their_own_work(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        _workflow, annotations = _submit(db_session, accounts, build_workflow)

        with pytest.raises(
            PermissionDeniedError,
            match=r"cannot review annotations they submitted themselves",
        ):
            AnnotationReviewService.submit_review(
                db_session,
                annotations[0].id,
                accounts["annotator"],
                "approved",
            )

    def test_approved_annotations_cannot_be_reviewed_again(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        _workflow, annotations = _submit(db_session, accounts, build_workflow)

        AnnotationReviewService.submit_review(
            db_session,
            annotations[0].id,
            accounts["dataset_owner"],
            "approved",
        )

        with pytest.raises(
            ConflictError,
            match=r"already been approved",
        ):
            AnnotationReviewService.submit_review(
                db_session,
                annotations[0].id,
                accounts["administrator"],
                "rejected",
            )

    def test_annotations_in_a_non_reviewable_state_are_rejected(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        _workflow, annotations = _submit(db_session, accounts, build_workflow)

        # No persisted annotation can hold a status outside the workflow set
        # (the table has a CHECK constraint), so this defensive branch of the
        # service is exercised with an in-memory state change only.
        annotations[0].status = "draft"

        with pytest.raises(
            ConflictError,
            match=r"cannot",
        ):
            AnnotationReviewService.submit_review(
                db_session,
                annotations[0].id,
                accounts["dataset_owner"],
                "approved",
            )

    def test_missing_annotations_are_reported(
        self,
        db_session,
        accounts,
    ):
        with pytest.raises(NotFoundError, match=r"Annotation not found\."):
            AnnotationReviewService.submit_review(
                db_session,
                999999,
                accounts["dataset_owner"],
                "approved",
            )


class TestReviewQueries:
    """Read helpers for the review history."""

    def test_reviews_are_retrievable_by_annotation_and_job(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow, annotations = _submit(db_session, accounts, build_workflow)

        review = AnnotationReviewService.submit_review(
            db_session,
            annotations[0].id,
            accounts["dataset_owner"],
            "needs_revision",
            comment="Please use the guideline label.",
        )

        assert AnnotationReviewService.get_review(db_session, review.id) is review
        assert AnnotationReviewService.require_review(db_session, review.id) is review
        assert len(AnnotationReviewService.get_reviews(db_session)) == 1
        assert (
            len(
                AnnotationReviewService.get_reviews_for_annotation(
                    db_session,
                    annotations[0].id,
                )
            )
            == 1
        )
        assert (
            len(
                AnnotationReviewService.get_reviews_for_job(
                    db_session,
                    workflow["job"].id,
                )
            )
            == 1
        )

    def test_missing_reviews_return_none_or_raise(self, db_session):
        assert AnnotationReviewService.get_review(db_session, 999999) is None

        with pytest.raises(NotFoundError, match=r"Annotation review not found\."):
            AnnotationReviewService.require_review(db_session, 999999)

        with pytest.raises(NotFoundError, match=r"Annotation review not found\."):
            AnnotationReviewService.delete_review(db_session, 999999)

    def test_reviews_can_be_deleted_for_correction(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        _workflow, annotations = _submit(db_session, accounts, build_workflow)

        review = AnnotationReviewService.submit_review(
            db_session,
            annotations[0].id,
            accounts["dataset_owner"],
            "rejected",
        )

        AnnotationReviewService.delete_review(db_session, review.id)

        assert AnnotationReviewService.get_review(db_session, review.id) is None
        assert AnnotationReviewService.get_reviews(db_session) == []
