"""Authentication endpoints: registration, login and profile."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_current_user
from backend.app.core.database import get_db
from backend.app.core.errors import AuthorizationError
from backend.app.core.logging import get_logger
from backend.app.core.security import create_access_token
from backend.app.models.user import User
from backend.app.schemas.auth import (
    LoginRequest,
    TokenResponse,
)
from backend.app.schemas.response import (
    APIResponse,
    success_response,
)
from backend.app.schemas.user import (
    UserCreate,
    UserResponse,
)
from backend.app.services.user_service import UserService

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new dataset owner or annotator account",
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
) -> APIResponse[UserResponse]:
    """Create a new account and return the public profile."""
    user = UserService.create_user(db, user_data)

    return success_response(
        UserResponse.model_validate(user),
        "Account created successfully. You can now sign in.",
    )


@router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    summary="Authenticate and receive a JWT access token",
)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
) -> APIResponse[TokenResponse]:
    """Validate credentials and issue a signed JWT."""
    user = UserService.authenticate_user(
        db,
        credentials.email,
        credentials.password,
    )

    if user is None:
        raise AuthorizationError("Invalid email or password.")

    token = create_access_token(
        user_id=user.id,
        email=user.email,
    )

    logger.info(
        "User %s logged in successfully.",
        user.email,
    )

    return success_response(
        TokenResponse(
            access_token=token,
            token_type="bearer",
        ),
        "Login successful.",
    )


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="Return the authenticated user profile",
)
def get_authenticated_user(
    current_user: User = Depends(get_current_user),
) -> APIResponse[UserResponse]:
    """Return the profile of the caller, including the role."""
    return success_response(
        UserResponse.model_validate(current_user),
        "Authenticated user profile.",
    )
