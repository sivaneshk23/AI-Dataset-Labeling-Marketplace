"""Shared FastAPI dependencies for authentication and authorisation."""

from collections.abc import Callable

from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.errors import (
    AuthorizationError,
    PermissionDeniedError,
)
from backend.app.core.roles import normalise_role
from backend.app.core.security import decode_access_token
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the authenticated user from the bearer token.

    Args:
        credentials: Bearer credentials extracted from the request.
        db: Active database session.

    Returns:
        The authenticated, active user.

    Raises:
        AuthorizationError: when the token is missing, invalid, expired or
            belongs to an unknown/inactive account.
    """
    if credentials is None or not credentials.credentials:
        raise AuthorizationError("Authentication credentials were not provided.")

    payload = decode_access_token(credentials.credentials)

    if payload is None:
        raise AuthorizationError("Invalid or expired token.")

    subject = payload.get("sub")

    if subject is None:
        raise AuthorizationError("Invalid token payload.")

    try:
        user_id = int(subject)
    except (TypeError, ValueError) as error:
        raise AuthorizationError("Invalid user identifier.") from error

    user = UserRepository.get_by_id(db, user_id)

    if user is None or not user.is_active:
        raise AuthorizationError("User not found or inactive.")

    return user


def require_roles(
    *allowed_roles: str,
) -> Callable[..., User]:
    """Build a dependency that restricts an endpoint to given roles.

    Args:
        *allowed_roles: Role names permitted to call the endpoint.

    Returns:
        A dependency returning the authenticated user.
    """
    permitted = {normalise_role(role) for role in allowed_roles}

    def role_dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:
        """Reject callers whose authenticated role is not permitted."""
        if current_user.role not in permitted:
            raise PermissionDeniedError(
                "You do not have permission to perform this action."
            )

        return current_user

    return role_dependency
