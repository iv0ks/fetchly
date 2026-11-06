"""Fetchly — personal document vault (intentionally vulnerable lab).

Fetchly is a tiny "personal document vault" web app. Signed-in users keep
their files (contracts, notes, invoices) in a private storage folder and can
preview or download any of them from the dashboard.

Under the hood the download endpoint builds a filesystem path by concatenating
a user-controlled filename onto the storage directory, with no validation.
That is the whole point of this lab: a textbook *path traversal* (CWE-22).

    GET /documents/download?doc=notes.txt        -> serves storage/notes.txt
    GET /documents/download?doc=../../etc/passwd  -> escapes the vault

This code is deliberately insecure. It exists ONLY to be run locally as a
practice target (e.g. with Burp Suite). Do NOT deploy it anywhere public and
do NOT reuse this pattern in real software. See README.md for the disclaimer.
"""

from __future__ import annotations

import os

from flask import Flask, Response, abort, render_template_string, request, send_file

app = Flask(__name__)

# Directory that is *supposed* to be the only place documents are served from.
# The vulnerability is that we never actually enforce this boundary.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")


# A couple of innocent-looking documents the "user" owns. These show up in the
# dashboard so the app behaves like a real product.
LISTED_DOCUMENTS = [
    "welcome.txt",
    "meeting-notes.txt",
    "q3-report.txt",
]


DASHBOARD_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Fetchly — Your documents</title>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 640px;
               margin: 3rem auto; padding: 0 1rem; color: #1a1a2e; }
        h1 { margin-bottom: 0.25rem; }
        p.sub { color: #555; margin-top: 0; }
        ul { list-style: none; padding: 0; }
        li { padding: 0.75rem 1rem; border: 1px solid #e0e0e0;
             border-radius: 8px; margin-bottom: 0.5rem; display: flex;
             justify-content: space-between; align-items: center; }
        a.btn { text-decoration: none; background: #3a0ca3; color: #fff;
                padding: 0.4rem 0.9rem; border-radius: 6px; font-size: 0.9rem; }
        code { background: #f2f2f7; padding: 0.1rem 0.3rem; border-radius: 4px; }
        footer { margin-top: 2rem; color: #888; font-size: 0.85rem; }
    </style>
</head>
<body>
    <h1>📁 Fetchly</h1>
    <p class="sub">Your personal document vault — welcome back, Alex.</p>
    <ul>
    {% for doc in documents %}
        <li>
            <span>📄 {{ doc }}</span>
            <a class="btn" href="/documents/download?doc={{ doc }}">Download</a>
        </li>
    {% endfor %}
    </ul>
    <footer>
        Fetchly v1.0 — files are served from your private vault via
        <code>/documents/download?doc=&lt;filename&gt;</code>.
    </footer>
</body>
</html>
"""


@app.get("/")
def dashboard() -> str:
    """Render the vault dashboard listing the user's documents."""
    return render_template_string(DASHBOARD_TEMPLATE, documents=LISTED_DOCUMENTS)


@app.get("/documents/download")
def download() -> Response:
    """Serve a document from the vault.

    VULNERABLE BY DESIGN: the ``doc`` parameter is joined onto STORAGE_DIR
    without any normalization or boundary check, so values like
    ``../../../../etc/passwd`` escape the intended directory (CWE-22).
    """
    doc = request.args.get("doc", "")
    if not doc:
        abort(400, description="Missing 'doc' query parameter.")

    # --- The vulnerable line -------------------------------------------------
    # os.path.join happily resolves '..' sequences, and we never verify that
    # the final path stays inside STORAGE_DIR before opening it.
    target_path = os.path.join(STORAGE_DIR, doc)
    # -------------------------------------------------------------------------

    if not os.path.isfile(target_path):
        abort(404, description=f"Document not found: {doc}")

    return send_file(target_path, as_attachment=False)


@app.get("/healthz")
def healthz() -> Response:
    """Liveness probe used by Docker's HEALTHCHECK."""
    return Response("ok", mimetype="text/plain")


if __name__ == "__main__":
    # Bind to all interfaces so the container is reachable; debug stays off.
    app.run(host="0.0.0.0", port=5000)  # noqa: S104 (intentional for the lab)
