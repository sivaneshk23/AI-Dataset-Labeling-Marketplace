from unittest.mock import MagicMock, patch

import pytest

from backend.app.models.user import User
from backend.app.schemas.user import UserCreate
from backend.app.services.user_service import UserService


def test_create_user_success(monkeypatch):
    db = MagicMock()

    user_data = UserCreate(
        name="Test Owner",
        email="owner@test.com",
        password="Password123",
    )

    monkeypatch.setattr(
        "backend.app.services.user_service.UserRepository.get_by_email",
        lambda db, email: None,
    )

    monkeypatch.setattr(
        "backend.app.services.user_service.hash_password",
        lambda password: "hashed_password",
    )

    created_user = User(
        id=1,
        name="Test Owner",
        email="owner@test.com",
        hashed_password="hashed_password",
        role="annotator",
        is_active=True,
    )

    monkeypatch.setattr(
        "backend.app.services.user_service.UserRepository.create",
        lambda db, user: created_user,
    )

    result = UserService.create_user(
        db,
        user_data,
    )

    assert result.id == 1
    assert result.email == "owner@test.com"
    assert result.hashed_password == "hashed_password"
    assert result.is_active is True


def test_create_user_duplicate_email():
    db = MagicMock()

    user_data = UserCreate(
        name="Duplicate User",
        email="existing@test.com",
        password="Password123",
    )

    existing_user = User(
        id=1,
        name="Existing User",
        email="existing@test.com",
        hashed_password="hashed_password",
        role="annotator",
        is_active=True,
    )

    with patch(
        "backend.app.services.user_service.UserRepository.get_by_email",
        return_value=existing_user,
    ):
        with pytest.raises(
            ValueError,
            match="A user with this email already exists.",
        ):
            UserService.create_user(
                db,
                user_data,
            )


def test_authenticate_user_success(monkeypatch):
    db = MagicMock()

    user = User(
        id=1,
        name="Test User",
        email="user@test.com",
        hashed_password="hashed_password",
        role="annotator",
        is_active=True,
    )

    monkeypatch.setattr(
        "backend.app.services.user_service.UserRepository.get_by_email",
        lambda db, email: user,
    )

    monkeypatch.setattr(
        "backend.app.services.user_service.verify_password",
        lambda password, hashed_password: True,
    )

    result = UserService.authenticate_user(
        db,
        "user@test.com",
        "Password123",
    )

    assert result is user


def test_authenticate_user_wrong_password(monkeypatch):
    db = MagicMock()

    user = User(
        id=1,
        name="Test User",
        email="user@test.com",
        hashed_password="hashed_password",
        role="annotator",
        is_active=True,
    )

    monkeypatch.setattr(
        "backend.app.services.user_service.UserRepository.get_by_email",
        lambda db, email: user,
    )

    monkeypatch.setattr(
        "backend.app.services.user_service.verify_password",
        lambda password, hashed_password: False,
    )

    result = UserService.authenticate_user(
        db,
        "user@test.com",
        "WrongPassword",
    )

    assert result is None


def test_authenticate_inactive_user(monkeypatch):
    db = MagicMock()

    user = User(
        id=1,
        name="Inactive User",
        email="inactive@test.com",
        hashed_password="hashed_password",
        role="annotator",
        is_active=False,
    )

    monkeypatch.setattr(
        "backend.app.services.user_service.UserRepository.get_by_email",
        lambda db, email: user,
    )

    result = UserService.authenticate_user(
        db,
        "inactive@test.com",
        "Password123",
    )

    assert result is None


def test_get_user(monkeypatch):
    db = MagicMock()

    user = User(
        id=5,
        name="Test User",
        email="user@test.com",
        hashed_password="hashed_password",
        role="annotator",
        is_active=True,
    )

    monkeypatch.setattr(
        "backend.app.services.user_service.UserRepository.get_by_id",
        lambda db, user_id: user,
    )

    result = UserService.get_user(
        db,
        5,
    )

    assert result is user


def test_get_users(monkeypatch):
    db = MagicMock()

    users = [
        User(
            id=1,
            name="Owner",
            email="owner@test.com",
            hashed_password="hashed_password",
            role="dataset_owner",
            is_active=True,
        ),
        User(
            id=2,
            name="Annotator",
            email="annotator@test.com",
            hashed_password="hashed_password",
            role="annotator",
            is_active=True,
        ),
    ]

    monkeypatch.setattr(
        "backend.app.services.user_service.UserRepository.get_all",
        lambda db: users,
    )

    result = UserService.get_users(db)

    assert len(result) == 2
    assert result[0].role == "dataset_owner"
    assert result[1].role == "annotator"