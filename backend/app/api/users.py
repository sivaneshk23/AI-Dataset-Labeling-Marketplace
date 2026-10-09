"""User administration and annotator directory endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import (
    get_current_user,
    require_roles,
)
from backend.app.core.database import get_db
from backend.app.core.roles import (
    ADMINISTRATOR,
    DATASET_OWNER,
)
from backend.app.models.user import User
from backend.app.schemas.response import (
    APIResponse,
    success_response,
)
from backend.app.schemas.user import (
    UserResponse,
    UserRoleUpdate,
    UserStatusUpdate,
)
from backend.app.services.user_service import UserService

router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)


@router.get(
    "",
    response_model=APIResponse[list[UserResponse]],
    summary="List every registered user (administrator only)",
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMINISTRATOR)),
) -> APIResponse[list[UserResponse]]:
    """Return all accounts for platform administration."""
    users = UserService.get_users(db)

    return success_response(
        [UserResponse.model_validate(user) for user in users],
        f"{len(users)} user account(s) returned.",
    )


@router.get(
    "/annotators",
    response_model=APIResponse[list[UserResponse]],
    summary="List annotator accounts available for assignment",
)
def get_annotators(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            DATASET_OWNER,
            ADMINISTRATOR,
        )
    ),
) -> APIResponse[list[UserResponse]]:
    """Return the annotator directory used by assignment screens."""
    annotators = UserService.get_annotators(
        db,
        active_only=active_only,
    )

    return success_response(
        [UserResponse.model_validate(annotator) for annotator in annotators],
        f"{len(annotators)} annotator(s) returned.",
    )


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="Return the authenticated user profile",
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
) -> APIResponse[UserResponse]:
    """Return the caller profile."""
    return success_response(
        UserResponse.model_validate(current_user),
        "Authenticated user profile.",
    )


@router.patch(
    "/{user_id}/role",
    response_model=APIResponse[UserResponse],
    summary="Change the role of an account (administrator only)",
)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMINISTRATOR)),
) -> APIResponse[UserResponse]:
    """Promote or demote an account."""
    user = UserService.update_role(
        db,
        user_id,
        payload.role,
        current_user,
    )

    return success_response(
        UserResponse.model_validate(user),
        "User role updated successfully.",
    )


@router.patch(
    "/{user_id}/status",
    response_model=APIResponse[UserResponse],
    summary="Activate or deactivate an account (administrator only)",
)
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMINISTRATOR)),
) -> APIResponse[UserResponse]:
    """Enable or disable an account."""
    user = UserService.set_active_status(
        db,
        user_id,
        payload.is_active,
        current_user,
    )

    state = "activated" if user.is_active else "deactivated"

    return success_response(
        UserResponse.model_validate(user),
        f"User account {state} successfully.",
    )


@router.delete(
    "/{user_id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Delete an account (administrator only)",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ADMINISTRATOR)),
) -> APIResponse[None]:
    """Remove an account from the platform."""
    UserService.delete_user(
        db,
        user_id,
        current_user,
    )

    return success_response(
        None,
        "User account deleted successfully.",
    )
