"""Scan attribution (/here) + storefront event logging (/events)."""
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.db import get_session
from app.models import Event, Place
from app.repo import placement_for_token
from app.schemas import EventIn

router = APIRouter(tags=["tracking"])


@router.get("/here/{qr_token}")
def scan(qr_token: str, session: Session = Depends(get_session)) -> RedirectResponse:
    """Log a scan for this surface, then 302 to the co-branded storefront."""
    placement = placement_for_token(session, qr_token)
    place = session.get(Place, placement.place_id)

    session.add(Event(placement_id=placement.id, kind="scan"))
    session.commit()

    target = (
        f"/guest-flow/01-map-storefront.html"
        f"?place={place.slug}&surface={placement.surface_slug}"
    )
    return RedirectResponse(url=target, status_code=302)


@router.post("/events", status_code=201)
def log_event(payload: EventIn, session: Session = Depends(get_session)) -> dict:
    placement = placement_for_token(session, payload.qrToken)
    session.add(Event(placement_id=placement.id, kind=payload.kind))
    session.commit()
    return {"ok": True, "kind": payload.kind}
