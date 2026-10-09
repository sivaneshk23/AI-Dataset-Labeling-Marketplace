from unittest.mock import MagicMock

import pytest

from backend.app.models.review import Review
from backend.app.services.review_service import ReviewService


def test_create_review(monkeypatch):
    db = MagicMock()

    job = MagicMock()

    created_review = Review(
        id=1,
        job_id=10,
        reviewer_id=5,
        rating=5,
        comment="Excellent work.",
    )

    monkeypatch.setattr(
        "backend.app.services.review_service.LabelingJobRepository.get_by_id",
        MagicMock(return_value=job),
    )

    create_mock = MagicMock(return_value=created_review)

    monkeypatch.setattr(
        "backend.app.services.review_service.ReviewRepository.create",
        create_mock,
    )

    result = ReviewService.create_review(
        db=db,
        job_id=10,
        reviewer_id=5,
        rating=5,
        comment="Excellent work.",
    )

    assert result is created_review

    created_object = create_mock.call_args.args[1]

    assert created_object.job_id == 10
    assert created_object.reviewer_id == 5
    assert created_object.rating == 5
    assert created_object.comment == "Excellent work."


def test_create_review_job_not_found(monkeypatch):
    db = MagicMock()

    monkeypatch.setattr(
        "backend.app.services.review_service.LabelingJobRepository.get_by_id",
        MagicMock(return_value=None),
    )

    with pytest.raises(
        ValueError,
        match=r"Labeling job not found\.",
    ):
        ReviewService.create_review(
            db=db,
            job_id=999999,
            reviewer_id=5,
            rating=5,
            comment="Test review.",
        )


def test_get_review(monkeypatch):
    db = MagicMock()

    review = MagicMock(spec=Review)

    get_mock = MagicMock(return_value=review)

    monkeypatch.setattr(
        "backend.app.services.review_service.ReviewRepository.get_by_id",
        get_mock,
    )

    result = ReviewService.get_review(
        db,
        1,
    )

    assert result is review

    get_mock.assert_called_once_with(
        db,
        1,
    )


def test_get_reviews(monkeypatch):
    db = MagicMock()

    reviews = [
        MagicMock(spec=Review),
        MagicMock(spec=Review),
    ]

    get_all_mock = MagicMock(return_value=reviews)

    monkeypatch.setattr(
        "backend.app.services.review_service.ReviewRepository.get_all",
        get_all_mock,
    )

    result = ReviewService.get_reviews(db)

    assert result == reviews

    get_all_mock.assert_called_once_with(
        db,
    )


def test_get_reviews_by_job(monkeypatch):
    db = MagicMock()

    reviews = [
        MagicMock(spec=Review),
    ]

    get_by_job_mock = MagicMock(return_value=reviews)

    monkeypatch.setattr(
        "backend.app.services.review_service.ReviewRepository.get_by_job",
        get_by_job_mock,
    )

    result = ReviewService.get_reviews_by_job(
        db,
        10,
    )

    assert result == reviews

    get_by_job_mock.assert_called_once_with(
        db,
        10,
    )


def test_update_review(monkeypatch):
    db = MagicMock()

    review = Review(
        id=1,
        job_id=10,
        reviewer_id=5,
        rating=3,
        comment="Old comment.",
    )

    monkeypatch.setattr(
        "backend.app.services.review_service.ReviewRepository.get_by_id",
        MagicMock(return_value=review),
    )

    update_mock = MagicMock(return_value=review)

    monkeypatch.setattr(
        "backend.app.services.review_service.ReviewRepository.update",
        update_mock,
    )

    result = ReviewService.update_review(
        db=db,
        review_id=1,
        rating=5,
        comment="Updated comment.",
    )

    assert result is review
    assert review.rating == 5
    assert review.comment == "Updated comment."

    update_mock.assert_called_once_with(
        db,
        review,
    )


def test_update_review_not_found(monkeypatch):
    db = MagicMock()

    monkeypatch.setattr(
        "backend.app.services.review_service.ReviewRepository.get_by_id",
        MagicMock(return_value=None),
    )

    with pytest.raises(
        ValueError,
        match=r"Review not found\.",
    ):
        ReviewService.update_review(
            db=db,
            review_id=999999,
            rating=5,
        )


def test_delete_review(monkeypatch):
    db = MagicMock()

    review = MagicMock(spec=Review)

    monkeypatch.setattr(
        "backend.app.services.review_service.ReviewRepository.get_by_id",
        MagicMock(return_value=review),
    )

    delete_mock = MagicMock()

    monkeypatch.setattr(
        "backend.app.services.review_service.ReviewRepository.delete",
        delete_mock,
    )

    result = ReviewService.delete_review(
        db,
        1,
    )

    assert result is None

    delete_mock.assert_called_once_with(
        db,
        review,
    )


def test_delete_review_not_found(monkeypatch):
    db = MagicMock()

    monkeypatch.setattr(
        "backend.app.services.review_service.ReviewRepository.get_by_id",
        MagicMock(return_value=None),
    )

    with pytest.raises(
        ValueError,
        match=r"Review not found\.",
    ):
        ReviewService.delete_review(
            db,
            999999,
        )
