"""Milestone 1 smoke: the app boots and serves the static frontend copy."""


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json().get("status") == "ok"


def test_frontend_is_served(client):
    """StaticFiles mounts demo/frontend at the site root."""
    resp = client.get("/partner-flow/00-landing.html")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
