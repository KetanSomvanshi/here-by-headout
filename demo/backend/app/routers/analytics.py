"""Screen 03 — per-surface funnel + totals. Replaces the hardcoded surfaceData object.

The whole dashboard collapses into aggregation over Event + Booking, grouped by
placement and joined back to the place. See ARCHITECTURE.md §4c.
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db import get_session
from app.models import Booking, Event
from app.repo import place_by_slug, placements_for_place
from app.utils import commission

router = APIRouter(tags=["analytics"])

# Event.kind is singular (impression|scan|chat|rec); the funnel keys are plural.
_KIND_TO_KEY = {"impression": "impressions", "scan": "scans", "chat": "chats", "rec": "recs"}
_COUNT_KEYS = tuple(_KIND_TO_KEY.values())


@router.get("/analytics/{slug}")
def analytics(slug: str, session: Session = Depends(get_session)) -> dict:
    place = place_by_slug(session, slug)
    placements = placements_for_place(session, place)

    surfaces = []
    totals = {k: 0 for k in _COUNT_KEYS}
    totals.update(bookings=0, gmv=0.0)

    for p in placements:
        events = session.exec(select(Event).where(Event.placement_id == p.id)).all()
        bookings = session.exec(select(Booking).where(Booking.placement_id == p.id)).all()

        counts = {key: 0 for key in _COUNT_KEYS}
        for e in events:
            key = _KIND_TO_KEY.get(e.kind)
            if key:
                counts[key] += 1
        gmv = round(sum(b.gmv for b in bookings), 2)

        row = {
            "surfaceSlug": p.surface_slug,
            "label": p.label,
            **counts,
            "bookings": len(bookings),
            "gmv": gmv,
            "commission": commission(gmv),
        }
        surfaces.append(row)

        for key in _COUNT_KEYS:
            totals[key] += counts[key]
        totals["bookings"] += len(bookings)
        totals["gmv"] += gmv

    totals["gmv"] = round(totals["gmv"], 2)
    totals["commission"] = commission(totals["gmv"])
    totals["conversion"] = round(totals["bookings"] / totals["scans"], 4) if totals["scans"] else 0

    return {
        "place": {"slug": place.slug, "placeName": place.name},
        "totals": totals,
        "surfaces": surfaces,
    }
