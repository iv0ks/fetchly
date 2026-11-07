"""Fetchly — personal document vault (intentionally vulnerable lab).

Fetchly is a tiny "personal document vault" web app. Signed-in users keep
their files (contracts, notes, invoices) in a private documents folder and can
preview or download any of them from the dashboard.

Under the hood the download endpoint builds a filesystem path by concatenating
a user-controlled filename onto the documents directory, with no validation.
That is the whole point of this lab: a textbook *path traversal* (CWE-22).

This module is just the application factory. The routes live in
``app.routes`` and the paths/configuration in ``app.config``.

This code is deliberately insecure. It exists ONLY to be run locally as a
practice target (e.g. with Burp Suite). Do NOT deploy it anywhere public and
do NOT reuse this pattern in real software. See README.md for the disclaimer.
"""

from __future__ import annotations

from flask import Flask, Response

from app.routes import bp, render_error


def create_app() -> Flask:
    """Application factory."""
    flask_app = Flask(__name__)
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
