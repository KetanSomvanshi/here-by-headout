"""Milestone 4 — the /here scan link (attribution) and storefront event logging."""
import pytest


def test_scan_redirects_to_storefront_with_attribution(client, place, tokens):
    token = tokens["lobby-table-tent"]
    resp = client.get(f"/here/{token}", follow_redirects=False)
    assert resp.status_code in (302, 307)
    loc = resp.headers["location"]
    assert "01-map-storefront.html" in loc
    assert f"place={place['slug']}" in loc
    assert "surface=lobby-table-tent" in loc


def test_scan_is_logged_for_that_surface(client, place, tokens):
    client.get(f"/here/{tokens['lobby-table-tent']}", follow_redirects=False)
    client.get(f"/here/{tokens['lobby-table-tent']}", follow_redirects=False)
    client.get(f"/here/{tokens['elevator']}", follow_redirects=False)

    surfaces = {s["surfaceSlug"]: s for s in client.get(f"/analytics/{place['slug']}").json()["surfaces"]}
    assert surfaces["lobby-table-tent"]["scans"] == 2
    assert surfaces["elevator"]["scans"] == 1
    assert surfaces["breakfast-counter"]["scans"] == 0


def test_unknown_token_scan_is_404(client):
    assert client.get("/here/not-a-real-token", follow_redirects=False).status_code == 404


@pytest.mark.parametrize("kind", ["impression", "chat", "rec"])
def test_event_kinds_accepted(client, tokens, kind):
    resp = client.post("/events", json={"qrToken": tokens["lobby-table-tent"], "kind": kind})
    assert resp.status_code == 201


def test_unknown_event_kind_rejected(client, tokens):
    resp = client.post("/events", json={"qrToken": tokens["lobby-table-tent"], "kind": "explode"})
    assert resp.status_code == 422


def test_event_unknown_token_is_404(client):
    resp = client.post("/events", json={"qrToken": "ghost", "kind": "chat"})
    assert resp.status_code == 404
