from sqlalchemy.orm import Session

from backend.app.core.security import (
    hash_password,
    verify_password,
)
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.user import UserCreate


class UserService:

    @staticmethod
    def create_user(
        db: Session,
        user_data: UserCreate
    ) -> User:

        existing_user = UserRepository.get_by_email(
            db,
            user_data.email
        )

        if existing_user is not None:
            raise ValueError(
                "A user with this email already exists."
            )

        user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hash_password(
                user_data.password
            ),
            is_active=True
        )

        return UserRepository.create(
            db,
            user
        )

    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str
    ) -> User | None:

        user = UserRepository.get_by_email(
            db,
            email
        )

        if user is None:
            return None

        if not user.is_active:
            return None

        if not verify_password(
            password,
            user.hashed_password
        ):
            return None

        return user

    @staticmethod
    def get_user(
        db: Session,
        user_id: int
    ) -> User | None:

        return UserRepository.get_by_id(
            db,
            user_id
        )
    @staticmethod
    def get_users(
        db: Session
    ) -> list[User]:

        return UserRepository.get_all(db)