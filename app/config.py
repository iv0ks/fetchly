"""Fetchly configuration — static defaults.

These are pure constants. The actual runtime paths (which depend on the
``DATA_ROOT`` env var) are resolved by the application factory in
``app.main.create_app`` and stored on ``app.config``, so nothing here reads the
environment at import time. That keeps the app easy to test: each ``create_app``
call can be pointed at a different data root.

Runtime layout (resolved in the factory):

    <data_root>/           <- DATA_ROOT      (holds flag.txt, the target)
    <data_root>/docs/      <- DOCUMENTS_DIR  (the served vault)
"""

from __future__ import annotations

import os

# Repo root is one level above the app/ package. Used as the DATA_ROOT default.
DEFAULT_DATA_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

# Name of the sub-directory (under DATA_ROOT) the app serves documents from.
DOCUMENTS_DIRNAME = "docs"

# The challenge flag. It is the *target* of the path traversal and lives at
# <DATA_ROOT>/flag.txt (one level above the served docs/). It is intentionally
# not committed to the repo; the app seeds it on startup if missing (and the
# Docker image also writes it at build time). Override via the FLAG env var.
FLAG_FILENAME = "flag.txt"
DEFAULT_FLAG = "FLAG{FETCHLY_UNLOCKED_THE_VAULT}"

# Documents shown on the dashboard so the app behaves like a real product.
LISTED_DOCUMENTS = [
    "welcome.txt",
    "meeting-notes.txt",
    "q3-report.txt",
]
