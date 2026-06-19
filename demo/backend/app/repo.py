"""Shared DB lookups + response builders used across routers."""
from fastapi import HTTPException
from sqlmodel import Session, select

from app.config import settings
from app.models import Place, Placement
from app.schemas import PlaceOut, PlacementOut


def placement_for_token(session: Session, qr_token: str) -> Placement:
    placement = session.exec(select(Placement).where(Placement.qr_token == qr_token)).first()
    if placement is None:
        raise HTTPException(status_code=404, detail="Unknown QR token")
    return placement


def place_by_slug(session: Session, slug: str) -> Place:
    place = session.exec(select(Place).where(Place.slug == slug)).first()
    if place is None:
        raise HTTPException(status_code=404, detail="Unknown place")
    return place


def placements_for_place(session: Session, place: Place) -> list[Placement]:
    return list(
        session.exec(
            select(Placement).where(Placement.place_id == place.id).order_by(Placement.created_at)
        )
    )


def build_place_out(place: Place, placements: list[Placement]) -> PlaceOut:
    return PlaceOut(
        slug=place.slug,
        placeName=place.name,
        placeType=place.type,
        location=place.location,
        placements=[
            PlacementOut(
                label=p.label,
                surfaceSlug=p.surface_slug,
                qrToken=p.qr_token,
                url=f"{settings.app_base_url}/here/{p.qr_token}",
            )
            for p in placements
        ],
    )
