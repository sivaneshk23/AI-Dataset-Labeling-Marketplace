from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.user import User


class UserRepository:

    @staticmethod
    def get_by_email(
        db: Session,
        email: str
    ) -> User | None:

        statement = select(User).where(
            User.email == email
        )

        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: int
    ) -> User | None:

        statement = select(User).where(
            User.id == user_id
        )

        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def create(
        db: Session,
        user: User
    ) -> User:

        db.add(user)
        db.commit()
        db.refresh(user)

        return user