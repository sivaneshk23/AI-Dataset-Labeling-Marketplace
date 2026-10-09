"""User ORM model and schema tests."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from backend.app.models.user import User
from backend.app.schemas.user import (
    UserCreate,
    UserResponse,
)


def test_user_table_structure():
    """The users table exposes the expected columns and constraints."""
    table = User.__table__

    expected_columns = {
        "id",
        "name",
        "email",
        "hashed_password",
        "role",
        "is_active",
        "created_at",
    }

    assert set(table.columns.keys()) == expected_columns

    assert table.c.id.primary_key is True
    assert table.c.email.unique is True
    assert table.c.name.nullable is False
    assert table.c.hashed_password.nullable is False


def test_valid_user_create_schema():
    """A valid registration payload is accepted."""
    user = UserCreate(
        name="Sivanesh",
        email="sivanesh@example.com",
        password="securepass123",
    )

    assert user.name == "Sivanesh"
    assert user.email == "sivanesh@example.com"
    assert user.password == "securepass123"
    assert user.role == "annotator"


def test_dataset_owner_role_can_self_register():
    """The dataset owner role is available during registration."""
    user = UserCreate(
        name="Owner",
        email="owner@example.com",
        password="securepass123",
        role="dataset-owner",
    )

    assert user.role == "dataset_owner"


def test_administrator_role_cannot_self_register():
    """Administrator accounts are created by an administrator only."""
    with pytest.raises(ValidationError):
        UserCreate(
            name="Owner",
            email="owner@example.com",
            password="securepass123",
            role="administrator",
        )


def test_invalid_role_is_rejected():
    """Unknown roles are rejected by the schema."""
    with pytest.raises(ValidationError):
        UserCreate(
            name="Owner",
            email="owner@example.com",
            password="securepass123",
            role="superuser",
        )


def test_invalid_email():
    """Malformed e-mail addresses are rejected."""
    with pytest.raises(ValidationError):
        UserCreate(
            name="Sivanesh",
            email="invalid-email",
            password="securepass123",
        )


def test_short_password():
    """Passwords shorter than eight characters are rejected."""
    with pytest.raises(ValidationError):
        UserCreate(
            name="Sivanesh",
            email="sivanesh@example.com",
            password="123",
        )


def test_user_response_schema_hides_password():
    """The public response schema never exposes the password hash."""
    orm_user = User(
        id=1,
        name="Sivanesh",
        email="sivanesh@example.com",
        hashed_password="hashed_password_value",
        role="annotator",
        is_active=True,
        created_at=datetime.now(UTC),
    )

    response = UserResponse.model_validate(orm_user)

    assert response.id == 1
    assert response.name == "Sivanesh"
    assert response.is_active is True
    assert not hasattr(response, "hashed_password")
