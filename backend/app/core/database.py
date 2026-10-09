from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base for all SQLAlchemy ORM models."""

    pass


def get_db():
    """Yield a database session and close it after the request."""
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def initialize_database() -> None:
    """Create any missing ORM tables before the API accepts requests.

    Render provisions an empty PostgreSQL database for a new deployment, while
    local developers may already have the Review-I tables.  ``create_all`` is
    intentionally additive: it preserves existing data and creates the
    annotation and AI tables introduced by later reviews.
    """
    from backend.app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
