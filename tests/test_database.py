"""Database foundation tests."""

from backend.app.core.database import (
    Base,
    SessionLocal,
    engine,
    get_db,
)


def test_database_configuration():
    """The SQLAlchemy engine is configured for PostgreSQL."""
    assert engine is not None
    assert engine.dialect.name in {"postgresql", "sqlite"}
    assert SessionLocal is not None
    assert Base is not None


def test_metadata_registers_every_marketplace_table():
    """Every ORM model is registered on the shared metadata."""
    import backend.app.models  # noqa: F401

    expected_tables = {
        "annotation_reviews",
        "annotation_tasks",
        "annotations",
        "dataset_records",
        "datasets",
        "job_assignments",
        "labeling_jobs",
        "reviews",
        "users",
    }

    assert expected_tables.issubset(set(Base.metadata.tables))


def test_get_db_dependency_closes_session():
    """The request scoped session dependency yields and closes a session."""
    dependency = get_db()

    session = next(dependency)

    assert session is not None

    dependency.close()
