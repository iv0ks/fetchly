"""Tests for Fetchly's download endpoint.

These document the app's behaviour executably:

* the *intended* path (downloading a listed document) works, and
* the *path traversal* (CWE-22) actually escapes the vault and reads the flag.

The exploit test is deliberately asserting that the vulnerability is present —
if someone "fixes" the bug, this test turns red and flags that the lab no
longer teaches what it claims to.
"""

from __future__ import annotations

import pytest

from app.main import create_app


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def test_dashboard_lists_documents(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"welcome.txt" in resp.data


def test_download_served_document(client):
    """The intended, happy-path download of a listed document works."""
    resp = client.get("/docs/download?file=welcome.txt")
    assert resp.status_code == 200
    # welcome.txt is a real file in docs/; just assert we got bytes back.
    assert resp.data


def test_path_traversal_reads_the_flag(client):
    """CWE-22: `../flag.txt` escapes docs/ and reads the flag (by design)."""
    resp = client.get("/docs/download?file=../flag.txt")
    assert resp.status_code == 200
    assert b"FLAG{" in resp.data


def test_missing_file_returns_styled_400(client):
    resp = client.get("/docs/download")
    assert resp.status_code == 400
    assert b"Fetchly" in resp.data  # styled error page, not raw Flask error


def test_unknown_file_returns_styled_404(client):
    resp = client.get("/docs/download?file=does-not-exist.txt")
    assert resp.status_code == 404
    assert b"Fetchly" in resp.data


def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.data == b"ok"
