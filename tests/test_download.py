"""Tests for Fetchly's document endpoint.

These document the app's behaviour executably:

* the *intended* path (downloading a listed document) works, and
* the *path traversal* (CWE-22) actually escapes the vault and reads the flag.

The exploit test is deliberately asserting that the vulnerability is present —
if someone "fixes" the bug, this test turns red and flags that the lab no
longer teaches what it claims to.

The flag does NOT live in the repo (it is created inside the Docker image at
build time). So the fixture builds a throwaway data root that mirrors the
runtime layout — ``<root>/docs/`` for served files and ``<root>/flag.txt`` as
the traversal target — and points the app at it via the ``DATA_ROOT`` env var.
Because the factory reads DATA_ROOT at call time, this needs no module reloads.
"""

from __future__ import annotations

import pytest

from app.main import create_app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    # Mirror the runtime layout inside a temp dir.
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "welcome.txt").write_text("hello from the vault\n")
    (docs_dir / "meeting-notes.txt").write_text("notes\n")
    (docs_dir / "q3-report.txt").write_text("report\n")
    (tmp_path / "flag.txt").write_text("FLAG{FETCHLY_UNLOCKED_THE_VAULT}\n")

    # Point the factory at the temp root (read at create_app() time).
    monkeypatch.setenv("DATA_ROOT", str(tmp_path))

    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def test_dashboard_lists_documents(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"welcome.txt" in resp.data


def test_download_served_document(client):
    """The intended, happy-path download of a listed document works."""
    resp = client.get("/docs?name=welcome.txt")
    assert resp.status_code == 200
    assert b"hello from the vault" in resp.data


def test_path_traversal_reads_the_flag(client):
    """CWE-22: `../flag.txt` escapes docs/ and reads the flag (by design)."""
    resp = client.get("/docs?name=../flag.txt")
    assert resp.status_code == 200
    assert b"FLAG{" in resp.data


def test_missing_name_returns_styled_400(client):
    resp = client.get("/docs")
    assert resp.status_code == 400
    assert b"Fetchly" in resp.data  # styled error page, not raw Flask error


def test_unknown_name_returns_styled_404(client):
    resp = client.get("/docs?name=does-not-exist.txt")
    assert resp.status_code == 404
    assert b"Fetchly" in resp.data


def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.data == b"ok"
