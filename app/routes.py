"""Fetchly HTTP routes.

The document endpoint is intentionally vulnerable: it joins a user-controlled
filename onto the configured documents directory with no validation, so values
like ``../flag.txt`` or ``../../etc/passwd`` escape the intended directory.
This is a textbook path traversal (CWE-22) and is the whole point of this lab.

    GET /docs?name=welcome.txt   -> serves docs/welcome.txt
    GET /docs?name=../flag.txt   -> escapes the vault (the flag)

Paths come from ``current_app.config`` (set by the factory), so the routes
don't read the environment or import mutable globals.

Do NOT reuse this pattern in real software. See README.md for the disclaimer.
"""

from __future__ import annotations

import os

from flask import (
    Blueprint,
    Response,
    current_app,
    render_template,
    request,
    send_file,
)

bp = Blueprint("fetchly", __name__)


@bp.get("/")
def dashboard() -> str:
    """Render the vault dashboard listing the user's documents."""
    documents = current_app.config["LISTED_DOCUMENTS"]
    return render_template("dashboard.html", documents=documents)


@bp.get("/docs")
def documents() -> Response:
    """Serve a document from the vault.

    VULNERABLE BY DESIGN: the ``name`` parameter is joined onto the documents
    directory without any normalization or boundary check, so values like
    ``../../../../etc/passwd`` escape the intended directory (CWE-22).
    """
    name = request.args.get("name", "")
    if not name:
        return render_error(400, "Missing 'name' query parameter.")

    documents_dir = current_app.config["DOCUMENTS_DIR"]

    # --- The vulnerable line -------------------------------------------------
    # os.path.join happily resolves '..' sequences, and we never verify that
    # the final path stays inside documents_dir before opening it.
    target_path = os.path.join(documents_dir, name)
    # -------------------------------------------------------------------------

    if not os.path.isfile(target_path):
        return render_error(404, f"Document not found: {name}")

    return send_file(target_path, as_attachment=False)


@bp.get("/healthz")
def healthz() -> Response:
    """Liveness probe used by Docker's HEALTHCHECK."""
    return Response("ok", mimetype="text/plain")


def render_error(status: int, message: str) -> Response:
    """Render the styled error page with the given status and message."""
    html = render_template("error.html", status=status, message=message)
    return Response(html, status=status, mimetype="text/html")
