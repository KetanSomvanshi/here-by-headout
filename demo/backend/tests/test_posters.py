"""Milestone 3 — replaces static PNGs + .txt export + 'unique link per spot' in 02."""


def test_one_poster_per_placement(client, place):
    resp = client.get(f"/places/{place['slug']}/posters")
    assert resp.status_code == 200
    posters = resp.json()["posters"]
    assert len(posters) == len(place["placements"])


def test_poster_metadata_links_to_png_and_token(client, place):
    posters = client.get(f"/places/{place['slug']}/posters").json()["posters"]
    setup_tokens = {p["qrToken"] for p in place["placements"]}
    for poster in posters:
        assert poster["qrToken"] in setup_tokens
        assert poster["png"].endswith(f"/posters/{poster['surfaceSlug']}.png")


def test_poster_image_is_real_png(client, place):
    surface = place["placements"][0]["surfaceSlug"]
    resp = client.get(f"/places/{place['slug']}/posters/{surface}.png")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/png"
    assert resp.content[:8] == b"\x89PNG\r\n\x1a\n", "must be PNG magic bytes"
    assert len(resp.content) > 1000, "should be a real composited image, not a stub"


def test_poster_for_unknown_surface_is_404(client, place):
    assert client.get(f"/places/{place['slug']}/posters/ghost.png").status_code == 404
