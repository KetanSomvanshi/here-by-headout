"""SQLModel tables — the data model in MASTER_PLAN.md §4 / ARCHITECTURE.md §3.

UUID string PKs (so a later Postgres swap is a connection-string change). The dashboard
funnel is a GROUP BY over Event + Booking, joined back to Placement → Place.
"""
from datetime import datetime, timezone
from uuid import uuid4

from sqlmodel import Field, SQLModel


def _uuid() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Partner(SQLModel, table=True):
    id: str = Field(default_factory=_uuid, primary_key=True)
    email: str | None = None
    created_at: datetime = Field(default_factory=_now)


class Place(SQLModel, table=True):
    id: str = Field(default_factory=_uuid, primary_key=True)
    partner_id: str | None = Field(default=None, foreign_key="partner.id")
    name: str
    type: str | None = None
    location: str
    slug: str = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=_now)


class Placement(SQLModel, table=True):
    id: str = Field(default_factory=_uuid, primary_key=True)
    place_id: str = Field(foreign_key="place.id", index=True)
    label: str
    surface_slug: str
    qr_token: str = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=_now)


class Event(SQLModel, table=True):
    id: str = Field(default_factory=_uuid, primary_key=True)
    placement_id: str = Field(foreign_key="placement.id", index=True)
    kind: str  # impression | scan | chat | rec
    created_at: datetime = Field(default_factory=_now)


class Booking(SQLModel, table=True):
    id: str = Field(default_factory=_uuid, primary_key=True)
    placement_id: str = Field(foreign_key="placement.id", index=True)
    experience: str
    gmv: float
    commission: float
    created_at: datetime = Field(default_factory=_now)
