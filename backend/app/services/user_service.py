"""Business logic for user accounts, roles and permissions."""

from sqlalchemy.orm import Session

from backend.app.core.errors import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from backend.app.core.logging import get_logger
from backend.app.core.roles import (
    ADMINISTRATOR,
    ALLOWED_ROLES,
    ANNOTATOR,
    DEFAULT_ROLE,
    is_valid_role,
    normalise_role,
)
from backend.app.core.security import (
    hash_password,
    verify_password,
)
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.user import UserCreate

logger = get_logger(__name__)


class UserService:
    """Account registration, authentication and administration."""

    @staticmethod
    def create_user(
        db: Session,
        user_data: UserCreate,
        role: str | None = None,
        allow_privileged: bool = False,
    ) -> User:
        """Create a user account.

        Args:
            db: Active database session.
            user_data: Validated registration payload.
            role: Optional role override, used by administrators.
            allow_privileged: When True, administrator accounts may be created.

        Returns:
            The persisted user.

        Raises:
            ConflictError: when the e-mail address is already registered.
            ValidationError: when the requested role is unknown.
            PermissionDeniedError: when a privileged role is not permitted.
        """
        requested_role = normalise_role(role or user_data.role or DEFAULT_ROLE)

        if not is_valid_role(requested_role):
            raise ValidationError(
                "Unsupported role. Allowed values: "
                + ", ".join(sorted(ALLOWED_ROLES))
                + "."
            )

        if requested_role == ADMINISTRATOR and not allow_privileged:
            raise PermissionDeniedError(
                "Administrator accounts can only be created by an "
                "existing administrator."
            )

        existing_user = UserRepository.get_by_email(
            db,
            user_data.email,
        )

        if existing_user is not None:
            raise ConflictError("A user with this email already exists.")

        user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            role=requested_role,
            is_active=True,
        )

        created = UserRepository.create(db, user)

        logger.info(
            "New user registered: %s (role=%s).",
            created.email,
            created.role,
        )

        return created

    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str,
    ) -> User | None:
        """Return the user when the credentials are valid."""
        user = UserRepository.get_by_email(db, email)

        if user is None:
            logger.warning(
                "Failed login attempt for unknown email %s.",
                email,
            )

            return None

        if not user.is_active:
            logger.warning(
                "Rejected login for inactive account %s.",
                email,
            )

            return None

        if not verify_password(
            password,
            user.hashed_password,
        ):
            logger.warning(
                "Failed login attempt for %s.",
                email,
            )

            return None

        return user

    @staticmethod
    def get_user(
        db: Session,
        user_id: int,
    ) -> User | None:
        """Return a user by identifier."""
        return UserRepository.get_by_id(db, user_id)

    @staticmethod
    def require_user(
        db: Session,
        user_id: int,
    ) -> User:
        """Return a user or raise :class:`NotFoundError`."""
        user = UserRepository.get_by_id(db, user_id)

        if user is None:
            raise NotFoundError("User not found.")

        return user

    @staticmethod
    def get_users(
        db: Session,
    ) -> list[User]:
        """Return every registered user."""
        return UserRepository.get_all(db)

    @staticmethod
    def get_annotators(
        db: Session,
        active_only: bool = True,
    ) -> list[User]:
        """Return the annotator accounts available for assignment."""
        return UserRepository.get_by_role(
            db,
            ANNOTATOR,
            active_only=active_only,
        )

    @staticmethod
    def update_role(
        db: Session,
        user_id: int,
        role: str,
        actor: User,
    ) -> User:
        """Change the role of an account.

        Raises:
            NotFoundError: when the user does not exist.
            ValidationError: when the role is unknown.
            PermissionDeniedError: when an administrator edits their own role.
        """
        normalised = normalise_role(role)

        if not is_valid_role(normalised):
            raise ValidationError(
                "Unsupported role. Allowed values: "
                + ", ".join(sorted(ALLOWED_ROLES))
                + "."
            )

        user = UserService.require_user(db, user_id)

        if user.id == actor.id:
            raise PermissionDeniedError("You cannot change your own role.")

        user.role = normalised

        updated = UserRepository.update(db, user)

        logger.info(
            "User %s role changed to %s by user %s.",
            updated.id,
            updated.role,
            actor.id,
        )

        return updated

    @staticmethod
    def set_active_status(
        db: Session,
        user_id: int,
        is_active: bool,
        actor: User,
    ) -> User:
        """Activate or deactivate an account."""
        user = UserService.require_user(db, user_id)

        if user.id == actor.id:
            raise PermissionDeniedError("You cannot deactivate your own account.")

        user.is_active = is_active

        updated = UserRepository.update(db, user)

        logger.info(
            "User %s active status set to %s by user %s.",
            updated.id,
            updated.is_active,
            actor.id,
        )

        return updated

    @staticmethod
    def delete_user(
        db: Session,
        user_id: int,
        actor: User,
    ) -> None:
        """Delete an account.

        Raises:
            PermissionDeniedError: when an administrator deletes themselves.
            ConflictError: when the last administrator account is targeted.
        """
        user = UserService.require_user(db, user_id)

        if user.id == actor.id:
            raise PermissionDeniedError("You cannot delete your own account.")

        if user.role == ADMINISTRATOR and UserRepository.count_all(db) <= 1:
            raise ConflictError("The last administrator account cannot be deleted.")

        UserRepository.delete(db, user)

        logger.info(
            "User %s deleted by user %s.",
            user_id,
            actor.id,
        )
