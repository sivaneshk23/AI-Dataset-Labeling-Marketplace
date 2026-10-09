"""Apply idempotent PostgreSQL migrations before a production release."""

from pathlib import Path

from sqlalchemy import text

from backend.app.core.database import engine

MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "database" / "migrations"


def _statements(sql: str) -> list[str]:
    """Split the project's simple idempotent DDL migrations into statements."""
    lines = [line for line in sql.splitlines() if not line.strip().startswith("--")]
    return [
        statement.strip()
        for statement in "\n".join(lines).split(";")
        if statement.strip()
    ]


def apply_migrations() -> None:
    """Apply every ordered migration exactly as stored in the repository."""
    if engine.dialect.name != "postgresql":
        return

    with engine.begin() as connection:
        for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
            for statement in _statements(path.read_text(encoding="utf-8")):
                connection.execute(text(statement))
            print(f"Applied migration: {path.name}")


if __name__ == "__main__":
    apply_migrations()
