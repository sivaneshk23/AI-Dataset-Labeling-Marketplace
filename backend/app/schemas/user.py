"""Validation schemas for platform users."""

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)

from backend.app.core.roles import (
    DEFAULT_ROLE,
    SELF_REGISTERABLE_ROLES,
    is_valid_role,
    normalise_role,
)


class UserBase(BaseModel):
    """Fields shared by user payloads."""

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        """Collapse whitespace in the display name."""
        cleaned = " ".join(value.split())

        if len(cleaned) < 2:
            raise ValueError("name must contain at least 2 characters.")

        return cleaned


class UserCreate(UserBase):
    """Payload used to register a new account."""

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    role: str = Field(
        default=DEFAULT_ROLE,
        max_length=30,
        description=(
            "Self-registration supports the dataset_owner and annotator "
            "roles. Administrator accounts are created by an administrator."
        ),
    )

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        """Ensure the requested role exists and may be self-registered."""
        normalised = normalise_role(value)

        if not is_valid_role(normalised):
            raise ValueError(
                "Unsupported role. Allowed values: "
                + ", ".join(sorted(SELF_REGISTERABLE_ROLES))
                + "."
            )

        if normalised not in SELF_REGISTERABLE_ROLES:
            raise ValueError("Administrator accounts cannot be self-registered.")

        return normalised


class UserRoleUpdate(BaseModel):
    """Payload used by an administrator to change a user role."""

    role: str = Field(max_length=30)

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        """Ensure the target role exists."""
        normalised = normalise_role(value)

        if not is_valid_role(normalised):
            raise ValueError(
                "Unsupported role. Allowed values: dataset_owner, "
                "annotator, administrator."
            )

        return normalised


class UserStatusUpdate(BaseModel):
    """Payload used by an administrator to activate or deactivate a user."""

    is_active: bool


class UserResponse(UserBase):
    """Public user representation returned by the API."""

    id: int
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
