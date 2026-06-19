"""Demo data loaded on startup so the dashboard opens populated.

Casa Aurelia Rome + its 4 placements, with funnel events and bookings whose GMV
reproduces the figures in 03-partner-dashboard.html (lobby 515, room 235, elevator 74,
breakfast 12 → total 836 GMV / €66.88 commission). Idempotent: skips if already seeded.
"""
import secrets

from sqlmodel import Session, select

from app.db import engine
from app.models import Booking, Event, Partner, Place, Placement
from app.utils import commission, slugify

PLACE_SLUG = "casa-aurelia-rome"

# label -> (scans, impressions, chats, recs, [booking gmvs])
_SURFACES = {
    "Lobby table-tent": (64, 58, 22, 18, [120.0, 215.0, 180.0]),   # 515
    "Guest room card": (41, 37, 14, 11, [95.0, 140.0]),           # 235
    "Breakfast counter": (9, 8, 3, 2, [12.0]),                    # 12
    "Elevator": (17, 15, 5, 4, [74.0]),                           # 74
}


def seed() -> None:
    with Session(engine) as session:
        if session.exec(select(Place).where(Place.slug == PLACE_SLUG)).first():
            return  # already seeded

        partner = Partner(email="host@casa-aurelia.example")
        session.add(partner)
        place = Place(
            partner_id=partner.id,
            name="Casa Aurelia Rome",
            type="Hotel",
            location="Via Germanico, Prati, Rome",
            slug=PLACE_SLUG,
        )
        session.add(place)

        experiences = ["Vatican Museums", "Colosseum Underground", "Borghese Gallery"]
        for label, (scans, impr, chats, recs, gmvs) in _SURFACES.items():
            placement = Placement(
                place_id=place.id,
                label=label,
                surface_slug=slugify(label),
                qr_token=secrets.token_urlsafe(9),
            )
            session.add(placement)

            for kind, n in (("scan", scans), ("impression", impr), ("chat", chats), ("rec", recs)):
                for _ in range(n):
                    session.add(Event(placement_id=placement.id, kind=kind))

            for i, gmv in enumerate(gmvs):
                session.add(Booking(
                    placement_id=placement.id,
                    experience=experiences[i % len(experiences)],
                    gmv=gmv,
                    commission=commission(gmv),
                ))

        session.commit()
