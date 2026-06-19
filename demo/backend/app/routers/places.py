"""Screen 01 — persist partner + place + placements; return slug + QR tokens."""
import secrets

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db import get_session
from app.models import Partner, Place, Placement
from app.repo import build_place_out, place_by_slug, placements_for_place
from app.schemas import PlaceCreate, PlaceOut
from app.utils import slugify

router = APIRouter(tags=["places"])


def _unique_slug(session: Session, base: str) -> str:
    """Make the place slug unique by suffixing -2, -3, … on collision."""
    slug, n = base, 1
    while session.exec(select(Place).where(Place.slug == slug)).first():
        n += 1
        slug = f"{base}-{n}"
    return slug


@router.post("/places", response_model=PlaceOut, status_code=201)
def create_place(payload: PlaceCreate, session: Session = Depends(get_session)) -> PlaceOut:
    partner = Partner(email=payload.email)
    session.add(partner)

    place = Place(
        partner_id=partner.id,
        name=payload.placeName,
        type=payload.placeType,
        location=payload.location,
        slug=_unique_slug(session, slugify(payload.placeName)),
    )
    session.add(place)

    placements = [
        Placement(
            place_id=place.id,
            label=label,
            surface_slug=slugify(label),
            qr_token=secrets.token_urlsafe(9),
        )
        for label in payload.placements
    ]
    session.add_all(placements)
    session.commit()

    for p in (place, *placements):
        session.refresh(p)
    return build_place_out(place, placements)


@router.get("/places/{slug}", response_model=PlaceOut)
def get_place(slug: str, session: Session = Depends(get_session)) -> PlaceOut:
    place = place_by_slug(session, slug)
    return build_place_out(place, placements_for_place(session, place))
