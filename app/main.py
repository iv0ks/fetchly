"""Fetchly — personal document vault (intentionally vulnerable lab).

Fetchly is a tiny "personal document vault" web app. Signed-in users keep
their files (contracts, notes, invoices) in a private documents folder and can
preview or download any of them from the dashboard.

Under the hood the document endpoint builds a filesystem path by concatenating
a user-controlled filename onto the documents directory, with no validation.
That is the whole point of this lab: a textbook *path traversal* (CWE-22).

This module is the application factory. It resolves the runtime data paths
(from the ``DATA_ROOT`` env var) and stores them on ``app.config``; the routes
read them from there. The route definitions live in ``app.routes`` and the
static defaults in ``app.config``.

This code is deliberately insecure. It exists ONLY to be run locally as a
practice target (e.g. with Burp Suite). Do NOT deploy it anywhere public and
do NOT reuse this pattern in real software. See README.md for the disclaimer.
"""

from __future__ import annotations

import os

from flask import Flask, Response

from app.config import (
    DEFAULT_DATA_ROOT,
    DEFAULT_FLAG,
    DOCUMENTS_DIRNAME,
    FLAG_FILENAME,
    LISTED_DOCUMENTS,
)
from app.routes import bp, render_error


def _seed_flag(data_root: str) -> None:
    """Create the challenge flag at <data_root>/flag.txt if it is missing.

    This is lab seeding, not application logic: it makes the challenge work the
    same whether you run the Docker image (which also writes the flag at build
    time) or start the app straight from Python, without ever committing the
    flag to the repo. The write is best-effort: under the container's read-only
    root filesystem the flag already exists, so a failed write here is fine.
    """
    flag_path = os.path.join(data_root, FLAG_FILENAME)
    if os.path.exists(flag_path):
        return
    flag_value = os.environ.get("FLAG", DEFAULT_FLAG)
    try:
        with open(flag_path, "w", encoding="utf-8") as fh:
            fh.write(flag_value + "\n")
    except OSError:
        # Read-only FS or similar — the flag is expected to already be present
        # in that case (e.g. baked into the Docker image). Nothing to do.
        pass


def create_app() -> Flask:
    """Application factory.

    Resolves the data paths at call time (not import time) so tests can point
    different instances at different data roots via the DATA_ROOT env var.
    """
    flask_app = Flask(__name__)

    # Root that holds both the served documents and the flag (the traversal
    # target). Defaults to the repo root; the Docker image sets DATA_ROOT=/app.
    data_root = os.environ.get("DATA_ROOT", DEFAULT_DATA_ROOT)
    flask_app.config["DATA_ROOT"] = data_root
    # Directory that is *supposed* to be the only place documents are served
    # from. The vulnerability is that we never actually enforce this boundary.
    flask_app.config["DOCUMENTS_DIR"] = os.path.join(data_root, DOCUMENTS_DIRNAME)
    flask_app.config["LISTED_DOCUMENTS"] = LISTED_DOCUMENTS

    # Make the lab self-contained: ensure the traversal target exists even when
    # running straight from Python (no Docker build step to create it).
    _seed_flag(data_root)

    flask_app.register_blueprint(bp)

    @flask_app.errorhandler(400)
    def bad_request(err: Exception) -> Response:
        return render_error(400, getattr(err, "description", "Bad request."))

    @flask_app.errorhandler(404)
    def not_found(err: Exception) -> Response:
        return render_error(404, getattr(err, "description", "Not found."))

    @flask_app.errorhandler(500)
    def server_error(err: Exception) -> Response:
        return render_error(500, "Internal server error.")

    return flask_app


# Module-level app for gunicorn ("app.main:app") and `flask --app app.main`.
app = create_app()


if __name__ == "__main__":
    # Bind to all interfaces so the container is reachable; debug stays off.
    app.run(host="0.0.0.0", port=5000)  # noqa: S104 (intentional for the lab)
