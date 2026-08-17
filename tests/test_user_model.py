from datetime import datetime

from pydantic import ValidationError

from backend.app.models.user import User
from backend.app.schemas.user import (
    UserCreate,
    UserResponse
)


def test_user_table_structure():
    table = User.__table__

    expected_columns = {
    "id",
    "name",
    "email",
    "hashed_password",
    "role",
    "is_active",
    "created_at"
}

    actual_columns = set(
        table.columns.keys()
    )

    assert actual_columns == expected_columns

    assert table.c.id.primary_key is True
    assert table.c.email.unique is True
    assert table.c.name.nullable is False
    assert table.c.hashed_password.nullable is False


def test_valid_user_create_schema():
    user = UserCreate(
        name="Sivanesh",
        email="sivanesh@example.com",
        password="securepass123"
    )

    assert user.name == "Sivanesh"
    assert user.email == "sivanesh@example.com"
    assert user.password == "securepass123"


def test_invalid_email():
    try:
        UserCreate(
            name="Sivanesh",
            email="invalid-email",
            password="securepass123"
        )

        assert False

    except ValidationError:
        pass


def test_short_password():
    try:
        UserCreate(
            name="Sivanesh",
            email="sivanesh@example.com",
            password="123"
        )

        assert False

    except ValidationError:
        pass


def test_user_response_schema():
    orm_user = User(
        id=1,
        name="Sivanesh",
        email="sivanesh@example.com",
        hashed_password="hashed_password_value",
        role="annotator",
        is_active=True,
        created_at=datetime.now()
    )

    response = UserResponse.model_validate(
        orm_user
    )

    assert response.id == 1
    assert response.name == "Sivanesh"
    assert response.is_active is True

    # Sensitive information must not appear
    # in the public response schema.
    assert not hasattr(
        response,
        "hashed_password"
    )


if __name__ == "__main__":
    tests = [
        (
            "User table structure",
            test_user_table_structure
        ),
        (
            "Valid user creation schema",
            test_valid_user_create_schema
        ),
        (
            "Invalid email validation",
            test_invalid_email
        ),
        (
            "Short password validation",
            test_short_password
        ),
        (
            "User response schema",
            test_user_response_schema
        )
    ]

    print(
        "\n===== USER MODEL AND SCHEMA TESTS =====\n"
    )

    passed = 0

    for name, test_function in tests:
        try:
            test_function()

            print(
                f"{name}: PASS"
            )

            passed += 1

        except Exception as error:
            print(
                f"{name}: FAIL"
            )

            print(
                "  Error:",
                repr(error)
            )

    print(
        f"\nResult: {passed}/{len(tests)} "
        "tests passed."
    )