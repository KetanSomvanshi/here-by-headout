"""Pure helpers, unit-tested for parity with the prototype's JS (see tests/unit)."""
import re

_NON_ALNUM = re.compile(r"[^a-z0-9]+")
COMMISSION_RATE = 0.08


def slugify(raw: str) -> str:
    """Lowercase, collapse runs of non-alphanumerics to single hyphens, trim.

    Mirrors the slug regex used in 02/03; falls back to "surface" when empty.
    """
    s = _NON_ALNUM.sub("-", raw.strip().lower()).strip("-")
    return s or "surface"


def commission(gmv: float) -> float:
    """Headout's take on a QR-attributed booking: 8% of GMV, rounded to cents."""
    return round(gmv * COMMISSION_RATE, 2)
