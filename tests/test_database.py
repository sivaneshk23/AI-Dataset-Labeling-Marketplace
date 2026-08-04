from backend.app.core.database import (
    Base,
    SessionLocal,
    engine
)


def test_database_configuration():
    print("\n===== DATABASE CONFIGURATION TEST =====")

    print(
        "SQLAlchemy engine:",
        engine.__class__.__name__
    )

    print(
        "Database dialect:",
        engine.dialect.name
    )

    print(
        "Session factory configured:",
        SessionLocal is not None
    )

    print(
        "Declarative base configured:",
        Base is not None
    )

    assert engine is not None
    assert engine.dialect.name == "postgresql"
    assert SessionLocal is not None
    assert Base is not None

    print(
        "\nDatabase configuration test passed."
    )


if __name__ == "__main__":
    test_database_configuration()