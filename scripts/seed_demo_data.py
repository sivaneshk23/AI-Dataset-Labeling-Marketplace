#!/usr/bin/env python3
"""Seed the marketplace with demo data from any working directory.

The real implementation lives in :mod:`backend.seed_demo_data`; this thin
runner exists so that operators, the Docker image and the deployment guide can
use one stable command from the repository root::

    python scripts/seed_demo_data.py

It is idempotent: running it twice only inserts the records that are missing.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow `python scripts/seed_demo_data.py` to import the `backend` package even
# though the interpreter's sys.path starts inside scripts/.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.seed_demo_data import seed  # noqa: E402  (path set up above)

if __name__ == "__main__":
    seed()
