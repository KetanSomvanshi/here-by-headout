"""Milestone 5 — replaces the random booking pings; pins commission attribution."""


def test_booking_computes_commission_at_8pct(client, tokens):
    resp = client.post("/bookings", json={
        "qrToken": tokens["lobby-table-tent"],
        "experience": "Vatican Museums",
        "gmv": 38.0,
    })
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["commission"] == 3.04            # round(38 * 0.08, 2)
    assert body["experience"] == "Vatican Museums"
    assert body["placement"]["surfaceSlug"] == "lobby-table-tent"


def test_booking_attributed_to_scanned_surface(client, place, tokens):
    client.post("/bookings", json={"qrToken": tokens["elevator"], "experience": "Colosseum", "gmv": 100.0})
    surfaces = {s["surfaceSlug"]: s for s in client.get(f"/analytics/{place['slug']}").json()["surfaces"]}
    assert surfaces["elevator"]["bookings"] == 1
    assert surfaces["elevator"]["commission"] == 8.0
    assert surfaces["lobby-table-tent"]["bookings"] == 0


def test_zero_or_negative_gmv_rejected(client, tokens):
    for bad in (0, -10):
        resp = client.post("/bookings", json={"qrToken": tokens["elevator"], "experience": "X", "gmv": bad})
        assert resp.status_code == 422


def test_booking_unknown_token_is_404(client):
    resp = client.post("/bookings", json={"qrToken": "ghost", "experience": "X", "gmv": 10})
    assert resp.status_code == 404
