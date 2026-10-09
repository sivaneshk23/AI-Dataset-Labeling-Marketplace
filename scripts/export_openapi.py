#!/usr/bin/env python3
"""Export the live OpenAPI contract to docs/openapi.json.

The capstone brief (Section 7.4) requires an API contract that is kept in step
with the as-built application. FastAPI generates that document from the code,
so this script is the single source of truth for the committed copy:

    python scripts/export_openapi.py

Run it after any router, schema or status-code change and commit the resulting
``docs/openapi.json``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.main import app  # noqa: E402  (path set up above)

OUTPUT = PROJECT_ROOT / "docs" / "openapi.json"


def export_openapi(output: Path = OUTPUT) -> Path:
    """Write the generated OpenAPI schema to ``output``.

    Args:
        output: Destination path for the JSON document.

    Returns:
        The path that was written.
    """
    output.parent.mkdir(parents=True, exist_ok=True)

    schema = app.openapi()

    output.write_text(
        json.dumps(schema, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )

    return output


if __name__ == "__main__":
    written = export_openapi()
    print(f"OpenAPI contract written to {written} ({len(app.routes)} routes).")
