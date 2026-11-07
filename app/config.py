"""Fetchly configuration — paths to the application's data.

Fetchly serves documents from a *documents directory* (``DOCUMENTS_DIR``). The
challenge's target file (``flag.txt``) deliberately lives one level *above*
that directory, so a path traversal can reach it.

Both locations derive from ``DATA_ROOT``:

    <data_root>/           <- DATA_ROOT      (holds flag.txt, the target)
    <data_root>/docs/      <- DOCUMENTS_DIR  (the served vault)

``DATA_ROOT`` can be overridden via the ``DATA_ROOT`` env var (the Docker image
sets it). Otherwise it falls back to the repo's ``./`` root, resolved relative
to this file:

    app/config.py  ->  ../   (repo root)
"""

from __future__ import annotations

import os

# Repo root is one level above the app/ package.
_DEFAULT_DATA_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

# Root that holds both the served documents and the flag (the traversal target).
DATA_ROOT = os.environ.get("DATA_ROOT", _DEFAULT_DATA_ROOT)

# Directory that is *supposed* to be the only place documents are served from.
# The vulnerability is that we never actually enforce this boundary.
DOCUMENTS_DIR = os.path.join(DATA_ROOT, "docs")

# Documents shown on the dashboard so the app behaves like a real product.
LISTED_DOCUMENTS = [
    "welcome.txt",
    "meeting-notes.txt",
    "q3-report.txt",
]
