"""Tests for the AI quality scoring rules (pure logic, no database)."""

from backend.app.services.ai.quality import (
    RECOMMENDATION_APPROVE,
    RECOMMENDATION_REVISE,
    QualityEngine,
)


def test_clean_annotation_is_recommended_for_approval():
    """A consistent, confident annotation scores full marks."""
    engine = QualityEngine(min_confidence=0.5)

    report = engine.evaluate(
        label="delivery",
        notes="Clear delivery complaint.",
        confidence=0.9,
        ai_suggested_label="Delivery",
        ai_confidence=0.8,
        label_counts={"delivery": 3},
        total_annotations=3,
    )

    assert report.score == 100.0
    assert report.recommendation == RECOMMENDATION_APPROVE
    assert report.agreement is True
    assert report.issues == ()


def test_short_label_is_high_severity_issue():
    """Labels that are too short cannot be exported as training data."""
    report = QualityEngine().evaluate(
        label="a",
        notes="note",
        confidence=0.9,
    )

    codes = {issue.code for issue in report.issues}

    assert "invalid_label" in codes
    assert report.score == 60.0
    assert report.recommendation == RECOMMENDATION_REVISE


def test_low_confidence_is_flagged():
    """Confidence below the threshold is reported to reviewers."""
    report = QualityEngine(min_confidence=0.8).evaluate(
        label="billing",
        notes="Invoice mismatch.",
        confidence=0.4,
    )

    assert [issue.code for issue in report.issues] == ["low_confidence"]
    assert report.score == 85.0


def test_ai_disagreement_is_flagged_only_for_confident_suggestions():
    """Disagreement with a weak AI suggestion is not penalised."""
    engine = QualityEngine()

    penalised = engine.evaluate(
        label="billing",
        notes="Invoice mismatch.",
        confidence=0.9,
        ai_suggested_label="delivery",
        ai_confidence=0.9,
    )

    tolerated = engine.evaluate(
        label="billing",
        notes="Invoice mismatch.",
        confidence=0.9,
        ai_suggested_label="delivery",
        ai_confidence=0.4,
    )

    assert "ai_disagreement" in {issue.code for issue in penalised.issues}
    assert "ai_disagreement" not in {issue.code for issue in tolerated.issues}


def test_agreement_is_none_without_ai_suggestion():
    """Without an AI suggestion agreement cannot be measured."""
    report = QualityEngine().evaluate(
        label="delivery",
        notes="Parcel missing.",
        confidence=0.9,
    )

    assert report.agreement is None


def test_missing_notes_are_flagged():
    """Reviewers are warned when no notes were provided."""
    report = QualityEngine().evaluate(
        label="refund",
        confidence=0.9,
    )

    assert "missing_notes" in {issue.code for issue in report.issues}


def test_rare_label_is_flagged_in_large_jobs():
    """Long tail labels are reported once the job has enough labels."""
    report = QualityEngine().evaluate(
        label="outlier",
        notes="Rare intent.",
        confidence=0.9,
        label_counts={"delivery": 49, "outlier": 1},
        total_annotations=50,
    )

    assert "rare_label" in {issue.code for issue in report.issues}


def test_dominant_label_is_flagged():
    """A single label dominating the job suggests label bias."""
    report = QualityEngine().evaluate(
        label="delivery",
        notes="Everything is delivery.",
        confidence=0.9,
        label_counts={"delivery": 19, "billing": 1},
        total_annotations=20,
    )

    assert "dominant_label" in {issue.code for issue in report.issues}


def test_repetitive_submission_is_flagged():
    """Copy-pasted submissions are detected."""
    report = QualityEngine().evaluate(
        label="delivery",
        notes="same note",
        confidence=0.9,
        repeated_submissions=5,
    )

    assert "repetitive_submission" in {issue.code for issue in report.issues}


def test_score_never_drops_below_zero():
    """Penalties cannot produce a negative score."""
    report = QualityEngine(min_confidence=0.9).evaluate(
        label="x",
        confidence=0.1,
        ai_suggested_label="delivery",
        ai_confidence=0.9,
        label_counts={"delivery": 40, "other": 1},
        total_annotations=41,
        repeated_submissions=9,
    )

    assert report.score == 0.0
    assert report.recommendation == RECOMMENDATION_REVISE
