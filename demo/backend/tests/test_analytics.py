"""Milestone 6 — replaces the hardcoded surfaceData funnel + per-surface breakdown in 03.

Builds a known dataset through the public API, then asserts the aggregation exactly.
"""


def _seed_known_traffic(client, tokens):
    # scans: 3 lobby, 1 elevator
    for _ in range(3):
        client.get(f"/here/{tokens['lobby-table-tent']}", follow_redirects=False)
    client.get(f"/here/{tokens['elevator']}", follow_redirects=False)
    # storefront events
    client.post("/events", json={"qrToken": tokens["lobby-table-tent"], "kind": "impression"})
    client.post("/events", json={"qrToken": tokens["lobby-table-tent"], "kind": "chat"})
    client.post("/events", json={"qrToken": tokens["lobby-table-tent"], "kind": "rec"})
    # bookings: lobby gmv 100 -> comm 8.0 ; elevator gmv 50 -> comm 4.0
    client.post("/bookings", json={"qrToken": tokens["lobby-table-tent"], "experience": "Vatican", "gmv": 100.0})
    client.post("/bookings", json={"qrToken": tokens["elevator"], "experience": "Colosseum", "gmv": 50.0})


def test_totals_are_exact_sums(client, place, tokens):
    _seed_known_traffic(client, tokens)
    totals = client.get(f"/analytics/{place['slug']}").json()["totals"]
    assert totals["scans"] == 4
    assert totals["impressions"] == 1
    assert totals["chats"] == 1
    assert totals["recs"] == 1
    assert totals["bookings"] == 2
    assert totals["gmv"] == 150.0
    assert totals["commission"] == 12.0
    assert totals["conversion"] == 0.5          # round(2 / 4, 4)


def test_one_surface_row_per_placement(client, place, tokens):
    data = client.get(f"/analytics/{place['slug']}").json()
    assert len(data["surfaces"]) == len(place["placements"])
    assert {s["surfaceSlug"] for s in data["surfaces"]} == {p["surfaceSlug"] for p in place["placements"]}


def test_surface_rows_sum_to_totals(client, place, tokens):
    _seed_known_traffic(client, tokens)
    data = client.get(f"/analytics/{place['slug']}").json()
    assert sum(s["scans"] for s in data["surfaces"]) == data["totals"]["scans"]
    assert sum(s["bookings"] for s in data["surfaces"]) == data["totals"]["bookings"]
    assert round(sum(s["commission"] for s in data["surfaces"]), 2) == data["totals"]["commission"]


def test_conversion_zero_when_no_scans(client, place):
    totals = client.get(f"/analytics/{place['slug']}").json()["totals"]
    assert totals["scans"] == 0
    assert totals["conversion"] == 0


def test_analytics_unknown_place_is_404(client):
    assert client.get("/analytics/nope").status_code == 404
