"""Capture a booking + commission, attribute it to the scanned surface, fan out over SSE."""
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db import get_session
from app.events_bus import bus
from app.models import Booking
from app.repo import placement_for_token
from app.schemas import BookingIn
from app.utils import commission

router = APIRouter(tags=["bookings"])


@router.post("/bookings", status_code=201)
def create_booking(payload: BookingIn, session: Session = Depends(get_session)) -> dict:
    placement = placement_for_token(session, payload.qrToken)
    comm = commission(payload.gmv)

    booking = Booking(
        placement_id=placement.id,
        experience=payload.experience,
        gmv=payload.gmv,
        commission=comm,
    )
    session.add(booking)
    session.commit()
    session.refresh(booking)

    result = {
        "id": booking.id,
        "experience": booking.experience,
        "gmv": booking.gmv,
        "commission": booking.commission,
        "placement": {"surfaceSlug": placement.surface_slug, "label": placement.label},
    }
    # Live ping for any open dashboard (screen 03) — replaces the fake setInterval loop.
    bus.publish({"experience": booking.experience, "commission": booking.commission,
                 "gmv": booking.gmv, "surface": placement.surface_slug})
    return result
