"""Fetchly — personal document vault (intentionally vulnerable lab).

Fetchly is a tiny "personal document vault" web app. Signed-in users keep
their files (contracts, notes, invoices) in a private storage folder and can
preview or download any of them from the dashboard.

Under the hood the download endpoint builds a filesystem path by concatenating
a user-controlled filename onto the storage directory, with no validation.
That is the whole point of this lab: a textbook *path traversal* (CWE-22).

    GET /documents/download?doc=welcome.txt       -> serves lab/storage/welcome.txt
    GET /documents/download?doc=../flag.txt       -> escapes the vault (the flag)
    GET /documents/download?doc=../../etc/passwd  -> walks further up

This code is deliberately insecure. It exists ONLY to be run locally as a
practice target (e.g. with Burp Suite). Do NOT deploy it anywhere public and
do NOT reuse this pattern in real software. See README.md for the disclaimer.
"""

from __future__ import annotations

import os

from flask import Flask, Response, abort, render_template, request, send_file

# --- Locating the lab data ---------------------------------------------------
# The decoy documents live in  <lab>/storage  and the flag lives in  <lab>/flag.txt
# (one level ABOVE storage, so path traversal has a target).
#
# LAB_DIR can be overridden via env var (the Docker image sets it). Otherwise we
# fall back to the repo's ./lab directory, resolved relative to this file:
#   app/main.py  ->  ../lab
_DEFAULT_LAB_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, "lab")
)
LAB_DIR = os.environ.get("LAB_DIR", _DEFAULT_LAB_DIR)

# Directory that is *supposed* to be the only place documents are served from.
# The vulnerability is that we never actually enforce this boundary.
STORAGE_DIR = os.path.join(LAB_DIR, "storage")

# Documents shown on the dashboard so the app behaves like a real product.
LISTED_DOCUMENTS = [
    "welcome.txt",
    "meeting-notes.txt",
    "q3-report.txt",
]


def create_app() -> Flask:
    """Application factory."""
    flask_app = Flask(__name__)

    @flask_app.get("/")
    def dashboard() -> str:
        """Render the vault dashboard listing the user's documents."""
        return render_template("dashboard.html", documents=LISTED_DOCUMENTS)

    @flask_app.get("/documents/download")
    def download() -> Response:
        """Serve a document from the vault.

        VULNERABLE BY DESIGN: the ``doc`` parameter is joined onto STORAGE_DIR
        without any normalization or boundary check, so values like
        ``../../../../etc/passwd`` escape the intended directory (CWE-22).
        """
        doc = request.args.get("doc", "")
        if not doc:
            abort(400, description="Missing 'doc' query parameter.")

        # --- The vulnerable line ---------------------------------------------
        # os.path.join happily resolves '..' sequences, and we never verify
        # that the final path stays inside STORAGE_DIR before opening it.
        target_path = os.path.join(STORAGE_DIR, doc)
        # ---------------------------------------------------------------------

        if not os.path.isfile(target_path):
            abort(404, description=f"Document not found: {doc}")

        return send_file(target_path, as_attachment=False)

    @flask_app.get("/healthz")
    def healthz() -> Response:
        """Liveness probe used by Docker's HEALTHCHECK."""
        return Response("ok", mimetype="text/plain")

    return flask_app


# Module-level app for gunicorn ("app.main:app") and `flask --app app.main`.
app = create_app()


if __name__ == "__main__":
    # Bind to all interfaces so the container is reachable; debug stays off.
    app.run(host="0.0.0.0", port=5000)  # noqa: S104 (intentional for the lab)
