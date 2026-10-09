"""Data access layer for platform users."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.user import User


class UserRepository:
    """CRUD and lookup queries for :class:`User`."""

    @staticmethod
    def get_by_email(
        db: Session,
        email: str,
    ) -> User | None:
        """Return a user by e-mail address (case insensitive)."""
        statement = select(User).where(
            func.lower(User.email) == str(email).strip().lower()
        )

        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: int,
    ) -> User | None:
        """Return a user by primary key."""
        statement = select(User).where(User.id == user_id)

        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def get_all(
        db: Session,
    ) -> list[User]:
        """Return every user ordered by id."""
        statement = select(User).order_by(User.id)

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def get_by_role(
        db: Session,
        role: str,
        active_only: bool = False,
    ) -> list[User]:
        """Return every user holding a given role."""
        statement = select(User).where(User.role == role)

        if active_only:
            statement = statement.where(User.is_active.is_(True))

        statement = statement.order_by(User.name)

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def count_all(
        db: Session,
    ) -> int:
        """Return the total number of registered users."""
        return int(db.scalar(select(func.count(User.id))) or 0)

    @staticmethod
    def create(
        db: Session,
        user: User,
    ) -> User:
        """Persist a new user."""
        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def update(
        db: Session,
        user: User,
    ) -> User:
        """Persist changes made to a tracked user instance."""
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def delete(
        db: Session,
        user: User,
    ) -> None:
        """Delete a user account."""
        db.delete(user)
        db.commit()
