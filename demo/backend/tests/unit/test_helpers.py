"""Pure-function parity with the prototype's JS helpers.

`slugify` mirrors the JS in 02/03; `commission` mirrors `commission = gmv * 0.08`,
which reproduces the exact euro figures shown in 03-partner-dashboard.html.
"""
import pytest

from app.utils import slugify, commission

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Lobby table-tent", "lobby-table-tent"),
        ("Guest room card", "guest-room-card"),
        ("Casa Aurelia Rome", "casa-aurelia-rome"),
        ("  Pool deck stand  ", "pool-deck-stand"),
        ("Bar / lounge", "bar-lounge"),
        ("Café", "caf"),          # non-alnum stripped, matches the JS regex
        ("", "surface"),          # empty falls back to "surface"
        ("---", "surface"),
    ],
)
def test_slugify(raw, expected):
    assert slugify(raw) == expected


@pytest.mark.parametrize(
    "gmv,expected",
    [
        (836.0, 66.88),   # all QR spots total in the prototype
        (515.0, 41.20),   # lobby
        (235.0, 18.80),   # room
        (74.0, 5.92),     # elevator
        (12.0, 0.96),     # breakfast
        (38.0, 3.04),     # single Vatican booking
    ],
)
def test_commission_matches_prototype(gmv, expected):
    assert commission(gmv) == pytest.approx(expected, abs=0.005)


def test_commission_rounds_to_cents():
    assert commission(33.33) == round(33.33 * 0.08, 2)
