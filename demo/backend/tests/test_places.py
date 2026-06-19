"""Milestone 2 — replaces the sessionStorage setup + validation in 01-place-setup.html."""
from tests.conftest import SETUP


def test_create_place_returns_slug_and_placements(client):
    resp = client.post("/places", json=SETUP)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["slug"] == "casa-aurelia-rome"
    assert body["placeName"] == SETUP["placeName"]
    assert len(body["placements"]) == len(SETUP["placements"])


def test_each_placement_has_unique_token_and_link(place):
    tokens = [p["qrToken"] for p in place["placements"]]
    assert all(tokens), "every placement must get a token"
    assert len(set(tokens)) == len(tokens), "tokens must be unique per spot"
    for p in place["placements"]:
        assert p["url"].endswith(f"/here/{p['qrToken']}")
        assert p["surfaceSlug"]  # derived from the label


def test_surface_slugs_match_labels(place):
    by_label = {p["label"]: p["surfaceSlug"] for p in place["placements"]}
    assert by_label["Lobby table-tent"] == "lobby-table-tent"
    assert by_label["Breakfast counter"] == "breakfast-counter"


def test_get_place_by_slug(client, place):
    resp = client.get(f"/places/{place['slug']}")
    assert resp.status_code == 200
    assert resp.json()["slug"] == place["slug"]


def test_get_unknown_place_is_404(client):
    assert client.get("/places/nope-nope").status_code == 404


# ── validation parity with validateForm() in the prototype ──

def test_blank_place_name_rejected(client):
    bad = {**SETUP, "placeName": "   "}
    assert client.post("/places", json=bad).status_code == 422


def test_blank_location_rejected(client):
    bad = {**SETUP, "location": ""}
    assert client.post("/places", json=bad).status_code == 422


def test_empty_placements_rejected(client):
    bad = {**SETUP, "placements": []}
    assert client.post("/places", json=bad).status_code == 422
