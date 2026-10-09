"""Unit tests for the annotation submission business rules.

The suite runs against the shared in-memory database fixtures so every
service rule is verified together with the repository layer used in
production, which is what the Review-II coverage target measures.
"""

import pytest

from backend.app.core.errors import (
    ConflictError,
    InvalidStateError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from backend.app.services.annotation_review_service import (
    AnnotationReviewService,
)
from backend.app.services.annotation_service import AnnotationService

MATCHING_ITEM = "Refund request for the damaged order."
SIMILAR_ITEM = "Refund request for the damaged delivery."


def _submit(db_session, task, annotator, label="refund request"):
    """Submit one label through the service layer."""
    return AnnotationService.submit_annotation(
        db_session,
        task.id,
        annotator,
        label,
    )


class TestAnnotationSubmission:
    """Rules applied while a label is submitted."""

    def test_submission_normalises_the_label_and_advances_the_task(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = build_workflow(items=(MATCHING_ITEM,))
        task = workflow["tasks"][0]
        annotator = accounts["annotator"]

        annotation = AnnotationService.submit_annotation(
            db_session,
            task.id,
            annotator,
            "  refund     request  ",
            notes="customer wants the money back",
            confidence=0.82,
        )

        assert annotation.label == "refund request"
        assert annotation.notes == "customer wants the money back"
        assert annotation.confidence == 0.82
        assert annotation.status == "submitted"
        assert annotation.annotator_id == annotator.id
        assert task.status == "submitted"

    def test_submission_assigns_an_unassigned_task_to_the_annotator(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = build_workflow(items=(MATCHING_ITEM,), assign_to=None)
        task = workflow["tasks"][0]
        annotator = accounts["annotator"]

        assert task.assigned_to is None

        _submit(db_session, task, annotator)

        assert task.assigned_to == annotator.id

    def test_submission_stores_the_ai_pre_label_for_quality_metrics(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = build_workflow(items=(MATCHING_ITEM, SIMILAR_ITEM))
        first, second = workflow["tasks"]
        annotator = accounts["annotator"]

        _submit(db_session, first, annotator)

        annotation = _submit(db_session, second, annotator)

        assert annotation.ai_suggested_label == "refund request"
        assert annotation.ai_confidence is not None
        assert annotation.ai_confidence > 0

    def test_only_annotators_can_submit_labels(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = build_workflow(items=(MATCHING_ITEM,))

        with pytest.raises(
            PermissionDeniedError,
            match=r"Only annotator accounts can submit labels\.",
        ):
            AnnotationService.submit_annotation(
                db_session,
                workflow["tasks"][0].id,
                accounts["dataset_owner"],
                "refund request",
            )

    def test_inactive_annotators_cannot_submit_labels(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = build_workflow(items=(MATCHING_ITEM,))
        annotator = accounts["annotator"]
        annotator.is_active = False

        with pytest.raises(PermissionDeniedError, match=r"inactive"):
            _submit(db_session, workflow["tasks"][0], annotator)

    def test_tasks_assigned_to_another_annotator_are_protected(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = build_workflow(items=(MATCHING_ITEM,))

        with pytest.raises(
            PermissionDeniedError,
            match=r"assigned to another annotator",
        ):
            _submit(
                db_session,
                workflow["tasks"][0],
                accounts["second_annotator"],
            )

    def test_a_submitted_task_cannot_receive_a_second_label(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = build_workflow(items=(MATCHING_ITEM,))
        task = workflow["tasks"][0]
        annotator = accounts["annotator"]

        _submit(db_session, task, annotator)

        with pytest.raises(InvalidStateError, match=r"cannot"):
            _submit(db_session, task, annotator)

    @pytest.mark.parametrize("label", ["", " ", "x"])
    def test_labels_that_are_too_short_are_rejected(
        self,
        db_session,
        accounts,
        build_workflow,
        label,
    ):
        workflow = build_workflow(items=(MATCHING_ITEM,))

        with pytest.raises(
            ValidationError,
            match=r"at least 2 characters",
        ):
            AnnotationService.submit_annotation(
                db_session,
                workflow["tasks"][0].id,
                accounts["annotator"],
                label,
            )

    def test_unknown_tasks_are_reported(self, db_session, accounts):
        with pytest.raises(
            NotFoundError,
            match=r"Annotation task not found\.",
        ):
            AnnotationService.submit_annotation(
                db_session,
                999999,
                accounts["annotator"],
                "refund request",
            )


class TestAnnotationQueries:
    """Read helpers and their visibility rules."""

    def test_missing_annotations_return_none_or_raise(self, db_session):
        assert AnnotationService.get_annotation(db_session, 999999) is None

        with pytest.raises(NotFoundError, match=r"Annotation not found\."):
            AnnotationService.require_annotation(db_session, 999999)

    def test_annotators_only_see_their_own_annotations(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = build_workflow(items=(MATCHING_ITEM, SIMILAR_ITEM), assign_to=None)
        first, second = workflow["tasks"]

        _submit(db_session, first, accounts["annotator"])
        _submit(db_session, second, accounts["second_annotator"])

        own = AnnotationService.get_annotations_for_viewer(
            db_session,
            accounts["annotator"],
        )

        assert len(own) == 1
        assert own[0].annotator_id == accounts["annotator"].id
        assert [row.id for row in own] == [
            AnnotationService.get_annotations_for_task(db_session, first.id)[0].id
        ]

        everything = AnnotationService.get_annotations_for_viewer(
            db_session,
            accounts["dataset_owner"],
        )

        assert len(everything) == 2

        filtered = AnnotationService.get_annotations_for_viewer(
            db_session,
            accounts["dataset_owner"],
            job_id=workflow["job"].id,
        )

        assert len(filtered) == 2

        assert (
            len(
                AnnotationService.get_annotations_for_job(
                    db_session,
                    workflow["job"].id,
                )
            )
            == 2
        )


def _submitted(db_session, accounts, build_workflow):
    """Create a workflow with one submitted annotation."""
    workflow = build_workflow(items=(MATCHING_ITEM,))
    task = workflow["tasks"][0]

    annotation = AnnotationService.submit_annotation(
        db_session,
        task.id,
        accounts["annotator"],
        "refund request",
    )

    return workflow, task, annotation


class TestAnnotationRevision:
    """Rules applied when a label is corrected."""

    def test_annotators_can_revise_their_own_label(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        _workflow, _task, annotation = _submitted(
            db_session,
            accounts,
            build_workflow,
        )

        updated = AnnotationService.update_annotation(
            db_session,
            annotation.id,
            accounts["annotator"],
            label="  delivery   delay ",
            notes="",
            confidence=0.4,
        )

        assert updated.label == "delivery delay"
        assert updated.notes is None
        assert updated.confidence == 0.4
        assert updated.status == "submitted"

    def test_dataset_owners_can_correct_a_label(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        _workflow, _task, annotation = _submitted(
            db_session,
            accounts,
            build_workflow,
        )

        updated = AnnotationService.update_annotation(
            db_session,
            annotation.id,
            accounts["dataset_owner"],
            label="refund request",
        )

        assert updated.label == "refund request"

    def test_other_annotators_cannot_revise_a_label(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        _workflow, _task, annotation = _submitted(
            db_session,
            accounts,
            build_workflow,
        )

        with pytest.raises(
            PermissionDeniedError,
            match=r"only modify your own annotations",
        ):
            AnnotationService.update_annotation(
                db_session,
                annotation.id,
                accounts["second_annotator"],
                label="refund request",
            )

    def test_revision_rejects_short_labels(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        _workflow, _task, annotation = _submitted(
            db_session,
            accounts,
            build_workflow,
        )

        with pytest.raises(
            ValidationError,
            match=r"at least 2 characters",
        ):
            AnnotationService.update_annotation(
                db_session,
                annotation.id,
                accounts["annotator"],
                label=" ",
            )

    def test_approved_annotations_are_immutable(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        _workflow, _task, annotation = _submitted(
            db_session,
            accounts,
            build_workflow,
        )

        AnnotationReviewService.submit_review(
            db_session,
            annotation.id,
            accounts["dataset_owner"],
            "approved",
        )

        with pytest.raises(
            ConflictError,
            match=r"Approved annotations are immutable",
        ):
            AnnotationService.update_annotation(
                db_session,
                annotation.id,
                accounts["dataset_owner"],
                label="refund request",
            )


class TestAnnotationWithdrawal:
    """Rules applied when an annotation is withdrawn."""

    def test_withdrawing_reopens_the_task(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        _workflow, task, annotation = _submitted(
            db_session,
            accounts,
            build_workflow,
        )

        AnnotationService.delete_annotation(
            db_session,
            annotation.id,
            accounts["annotator"],
        )

        assert AnnotationService.get_annotation(db_session, annotation.id) is None
        assert task.status == "in_progress"

    def test_approved_annotations_cannot_be_withdrawn(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        _workflow, _task, annotation = _submitted(
            db_session,
            accounts,
            build_workflow,
        )

        AnnotationReviewService.submit_review(
            db_session,
            annotation.id,
            accounts["dataset_owner"],
            "approved",
        )

        with pytest.raises(
            ConflictError,
            match=r"Approved annotations cannot be deleted",
        ):
            AnnotationService.delete_annotation(
                db_session,
                annotation.id,
                accounts["dataset_owner"],
            )

    def test_other_annotators_cannot_withdraw_a_label(
        self,
        db_session,
        accounts,
        build_workflow,
    ):
        _workflow, _task, annotation = _submitted(
            db_session,
            accounts,
            build_workflow,
        )

        with pytest.raises(PermissionDeniedError):
            AnnotationService.delete_annotation(
                db_session,
                annotation.id,
                accounts["second_annotator"],
            )
