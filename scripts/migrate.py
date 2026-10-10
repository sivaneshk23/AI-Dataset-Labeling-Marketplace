"""Initialize the base schema, then apply ordered PostgreSQL migrations."""

from pathlib import Path

from sqlalchemy import text

from backend.app.core.database import engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"
MIGRATIONS_DIR = PROJECT_ROOT / "database" / "migrations"


def _statements(sql: str) -> list[str]:
    """Split the project's simple SQL files into individual statements."""
    lines = [line for line in sql.splitlines() if not line.strip().startswith("--")]
    return [
        statement.strip()
        for statement in "\n".join(lines).split(";")
        if statement.strip()
    ]


def apply_migrations() -> None:
    """Create the base schema first, then apply additive migrations."""
    if engine.dialect.name != "postgresql":
        return

    with engine.begin() as connection:
        if not SCHEMA_PATH.is_file():
            raise FileNotFoundError(f"Base database schema not found: {SCHEMA_PATH}")

        for statement in _statements(SCHEMA_PATH.read_text(encoding="utf-8")):
            connection.execute(text(statement))
        print(f"Applied base schema: {SCHEMA_PATH.name}")

        for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
            for statement in _statements(path.read_text(encoding="utf-8")):
                connection.execute(text(statement))
            print(f"Applied migration: {path.name}")


if __name__ == "__main__":
    apply_migrations()
