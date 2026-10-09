"""Unit tests for the AI assisted annotation enhancement (Day 42-59).

The enhancement must work with zero external dependencies, so the tests force
the offline similarity provider. That keeps the suite deterministic in CI while
still covering the graceful-degradation path and the quality insights that are
surfaced to dataset owners.
"""

import pytest

from backend.app.core.config import settings
from backend.app.core.errors import (
    ExternalServiceError,
    NotFoundError,
)
from backend.app.services.ai import (
    LOCAL_PROVIDER,
    LabelledExample,
    LocalSimilarityProvider,
    reset_provider_cache,
)
from backend.app.services.ai_service import AIService
from backend.app.services.annotation_service import AnnotationService

REFUND_ITEM = "Refund request for the damaged order."
REFUND_ITEM_2 = "Refund request for the damaged delivery."
DELAY_ITEM = "Delivery driver left the parcel at the front door."


@pytest.fixture()
def offline_ai(monkeypatch):
    """Force the offline provider so no API key is needed in CI."""
    monkeypatch.setattr(settings, "ai_provider", LOCAL_PROVIDER)
    monkeypatch.setattr(settings, "gemini_api_key", "")

    reset_provider_cache()

    yield

    reset_provider_cache()


def _labelled_job(db_session, accounts, build_workflow, labels=None):
    """Submit the given labels for a two record job."""
    workflow = build_workflow(items=(REFUND_ITEM, DELAY_ITEM))
    labels = labels or ("refund request", "delivery delay")

    annotations = [
        AnnotationService.submit_annotation(
            db_session,
            task.id,
            accounts["annotator"],
            label,
            confidence=0.9,
        )
        for task, label in zip(workflow["tasks"], labels, strict=True)
    ]

    return workflow, annotations


class TestProviderConfiguration:
    """Provider registry behaviour."""

    def test_the_offline_engine_is_used_without_an_api_key(self, offline_ai):
        assert AIService.provider_name() == LocalSimilarityProvider.name
        assert AIService.uses_external_provider() is False

    def test_the_local_provider_returns_an_empty_suggestion_without_input(self):
        suggestion = LocalSimilarityProvider().suggest("   ", (), ())

        assert suggestion.label == ""
        assert suggestion.confidence == 0.0
        assert "usable text tokens" in suggestion.rationale

    def test_the_local_provider_reports_when_no_labels_exist_yet(self):
        suggestion = LocalSimilarityProvider().suggest(
            REFUND_ITEM,
            (),
            (),
        )

        assert suggestion.label == ""
        assert "Approve at least one annotation" in suggestion.rationale


class TestLabelSuggestions:
    """Pre-labelling suggestions produced for annotators."""

    def test_suggestions_use_the_declared_candidate_labels(
        self,
        offline_ai,
        db_session,
        build_workflow,
    ):
        workflow = build_workflow(items=(REFUND_ITEM,), assign_to=None)

        suggestion = AIService.suggest_label(
            db_session,
            workflow["job"].id,
            REFUND_ITEM,
            candidate_labels=["refund request", "delivery delay"],
        )

        assert suggestion.label == "refund request"
        assert 0 < suggestion.confidence <= 1
        assert suggestion.provider == LocalSimilarityProvider.name
        assert "candidate labels" in suggestion.rationale
        assert isinstance(suggestion.alternatives, tuple)

    def test_suggestions_learn_from_already_submitted_labels(
        self,
        offline_ai,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow, _annotations = _labelled_job(
            db_session,
            accounts,
            build_workflow,
        )

        suggestion = AIService.suggest_label(
            db_session,
            workflow["job"].id,
            REFUND_ITEM_2,
        )

        assert suggestion.label == "refund request"
        assert suggestion.confidence >= settings.ai_min_confidence
        assert suggestion.confidence > 0.55

    def test_candidate_labels_merge_declared_and_observed_labels(
        self,
        offline_ai,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow, _annotations = _labelled_job(
            db_session,
            accounts,
            build_workflow,
        )

        labels = AIService.candidate_label_set(
            db_session,
            workflow["job"].id,
            extra_labels=["Refund Request", "  ", "Delivery delay"],
        )

        assert {label.lower() for label in labels} == {
            "refund request",
            "delivery delay",
        }

    def test_training_examples_ignore_rejected_work(
        self,
        offline_ai,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow, annotations = _labelled_job(
            db_session,
            accounts,
            build_workflow,
        )

        annotations[1].status = "rejected"
        db_session.flush()

        examples = AIService.approved_examples(
            db_session,
            workflow["job"].id,
        )

        assert examples == (
            LabelledExample(input_text=REFUND_ITEM, label="refund request"),
        )

    def test_suggestions_require_an_existing_job(self, offline_ai, db_session):
        with pytest.raises(NotFoundError, match=r"Labeling job not found\."):
            AIService.suggest_label(db_session, 999999, REFUND_ITEM)

    def test_provider_failures_degrade_to_the_offline_engine(
        self,
        offline_ai,
        db_session,
        build_workflow,
        monkeypatch,
    ):
        class FailingProvider:
            """Stand-in for an unreachable external AI provider."""

            name = "gemini"
            is_external = True

            def suggest(self, input_text, candidate_labels, examples):
                raise ExternalServiceError("Gemini is unreachable.")

        workflow = build_workflow(items=(REFUND_ITEM,), assign_to=None)

        monkeypatch.setattr(
            "backend.app.services.ai_service.get_provider",
            FailingProvider,
        )

        assert AIService.uses_external_provider() is True

        suggestion = AIService.suggest_label(
            db_session,
            workflow["job"].id,
            REFUND_ITEM,
            candidate_labels=["refund request"],
        )

        assert suggestion.provider == LocalSimilarityProvider.name
        assert suggestion.label == "refund request"


class TestQualityInsights:
    """Quality scoring exposed to reviewers and dataset owners."""

    def test_quality_reports_describe_a_submitted_annotation(
        self,
        offline_ai,
        db_session,
        accounts,
        build_workflow,
    ):
        _workflow, annotations = _labelled_job(
            db_session,
            accounts,
            build_workflow,
        )

        report = AIService.evaluate_annotation(db_session, annotations[0])

        assert 0 <= report.score <= 100
        assert isinstance(report.recommendation, str)
        assert report.recommendation
        assert report.agreement in (None, True, False)
        assert isinstance(report.issues, tuple)

    def test_short_labels_are_flagged_with_a_severity(
        self,
        offline_ai,
        db_session,
        accounts,
        build_workflow,
    ):
        _workflow, annotations = _labelled_job(
            db_session,
            accounts,
            build_workflow,
        )
        annotations[0].label = "x"

        report = AIService.evaluate_annotation(db_session, annotations[0])

        assert report.issues
        assert {issue.severity for issue in report.issues} & {
            "high",
            "medium",
            "low",
        }
        assert report.score < 100

    def test_repeated_submissions_are_counted(
        self,
        offline_ai,
        db_session,
        accounts,
        build_workflow,
    ):
        _workflow, annotations = _labelled_job(
            db_session,
            accounts,
            build_workflow,
            labels=("refund request", "refund request"),
        )

        assert AIService.count_repetitions(db_session, annotations[1]) == 2

    def test_missing_tasks_cannot_be_scored(self, offline_ai, db_session):
        from backend.app.models.annotation import Annotation

        with pytest.raises(NotFoundError, match=r"Annotation task not found\."):
            AIService.evaluate_annotation(
                db_session,
                Annotation(
                    task_id=999999,
                    annotator_id=1,
                    label="refund request",
                    status="submitted",
                ),
            )

    def test_job_insights_aggregate_the_quality_metrics(
        self,
        offline_ai,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow, _annotations = _labelled_job(
            db_session,
            accounts,
            build_workflow,
        )

        insights = AIService.job_insights(db_session, workflow["job"].id)

        assert set(insights) == {
            "job_id",
            "provider",
            "total_annotations",
            "labelled_tasks",
            "unlabelled_tasks",
            "label_distribution",
            "agreement_rate",
            "average_confidence",
            "ai_coverage",
            "duplicate_annotations",
            "flagged_annotations",
            "annotator_stats",
            "recommendations",
        }

        assert insights["job_id"] == workflow["job"].id
        assert insights["provider"] == LocalSimilarityProvider.name
        assert insights["total_annotations"] == 2
        assert insights["labelled_tasks"] == 2
        assert insights["unlabelled_tasks"] == 0
        assert insights["average_confidence"] == 0.9
        assert 0 <= insights["ai_coverage"] <= 100
        assert isinstance(insights["recommendations"], list)
        assert insights["recommendations"]

        labels = {entry["label"] for entry in insights["label_distribution"]}

        assert labels == {"refund request", "delivery delay"}

        for entry in insights["label_distribution"]:
            assert 0 <= entry["share"] <= 100

        for stats in insights["annotator_stats"]:
            assert stats["annotations"] >= 1

    def test_insights_report_unlabelled_work(
        self,
        offline_ai,
        db_session,
        accounts,
        build_workflow,
    ):
        workflow = build_workflow(items=(REFUND_ITEM, DELAY_ITEM))

        AnnotationService.submit_annotation(
            db_session,
            workflow["tasks"][0].id,
            accounts["annotator"],
            "refund request",
        )

        insights = AIService.job_insights(db_session, workflow["job"].id)

        assert insights["total_annotations"] == 1
        assert insights["unlabelled_tasks"] == 1
        assert insights["recommendations"]

    def test_insights_require_an_existing_job(self, offline_ai, db_session):
        with pytest.raises(NotFoundError, match=r"Labeling job not found\."):
            AIService.job_insights(db_session, 999999)
