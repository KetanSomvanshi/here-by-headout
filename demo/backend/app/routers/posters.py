"""Screen 02 — branded QR poster metadata + the composited PNGs themselves."""
from fastapi import APIRouter, Depends, Response
from sqlmodel import Session

from app.db import get_session
from app.repo import place_by_slug, placements_for_place
from app.services.posters import build_poster_png

router = APIRouter(tags=["posters"])


@router.get("/places/{slug}/posters")
def list_posters(slug: str, session: Session = Depends(get_session)) -> dict:
    place = place_by_slug(session, slug)
    placements = placements_for_place(session, place)
    return {
        "posters": [
            {
                "placement": p.label,
                "surfaceSlug": p.surface_slug,
                "qrToken": p.qr_token,
                "png": f"/places/{slug}/posters/{p.surface_slug}.png",
            }
            for p in placements
        ]
    }


@router.get("/places/{slug}/posters/{surface_slug}.png")
def poster_png(slug: str, surface_slug: str, session: Session = Depends(get_session)) -> Response:
    place = place_by_slug(session, slug)
    placements = placements_for_place(session, place)
    for index, p in enumerate(placements):
        if p.surface_slug == surface_slug:
            png = build_poster_png(p.qr_token, index)
            return Response(content=png, media_type="image/png")
    return Response(status_code=404)
