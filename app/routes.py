"""Fetchly HTTP routes.

The download endpoint is intentionally vulnerable: it joins a user-controlled
filename onto ``DOCUMENTS_DIR`` with no validation, so values like
``../flag.txt`` or ``../../etc/passwd`` escape the intended directory. This is
a textbook path traversal (CWE-22) and is the whole point of this lab.

    GET /docs/download?file=welcome.txt   -> serves docs/welcome.txt
    GET /docs/download?file=../flag.txt   -> escapes the vault (the flag)

Do NOT reuse this pattern in real software. See README.md for the disclaimer.
"""

from __future__ import annotations

import os

from flask import (
    Blueprint,
    Response,
    render_template,
    request,
    send_file,
)

from app.config import DOCUMENTS_DIR, LISTED_DOCUMENTS

bp = Blueprint("fetchly", __name__)


@bp.get("/")
def dashboard() -> str:
    """Render the vault dashboard listing the user's documents."""
    return render_template("dashboard.html", documents=LISTED_DOCUMENTS)


@bp.get("/docs/download")
def download() -> Response:
    """Serve a document from the vault.

    VULNERABLE BY DESIGN: the ``file`` parameter is joined onto DOCUMENTS_DIR
    without any normalization or boundary check, so values like
    ``../../../../etc/passwd`` escape the intended directory (CWE-22).
    """
    file = request.args.get("file", "")
    if not file:
        return render_error(400, "Missing 'file' query parameter.")

    # --- The vulnerable line -------------------------------------------------
    # os.path.join happily resolves '..' sequences, and we never verify that
    # the final path stays inside DOCUMENTS_DIR before opening it.
    target_path = os.path.join(DOCUMENTS_DIR, file)
    # -------------------------------------------------------------------------

    if not os.path.isfile(target_path):
        return render_error(404, f"Document not found: {file}")

    return send_file(target_path, as_attachment=False)


@bp.get("/healthz")
def healthz() -> Response:
    """Liveness probe used by Docker's HEALTHCHECK."""
    return Response("ok", mimetype="text/plain")


def render_error(status: int, message: str) -> Response:
    """Render the styled error page with the given status and message."""
    html = render_template("error.html", status=status, message=message)
    return Response(html, status=status, mimetype="text/html")
