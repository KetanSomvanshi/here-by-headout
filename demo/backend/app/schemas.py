"""Request/response models. Keys are camelCase to match the prototype's JS."""
from pydantic import BaseModel, field_validator

EVENT_KINDS = {"impression", "chat", "rec"}


def _require_nonblank(v: str) -> str:
    if not isinstance(v, str) or not v.strip():
        raise ValueError("must not be blank")
    return v.strip()


class PlaceCreate(BaseModel):
    placeName: str
    location: str
    placements: list[str]
    placeType: str | None = None
    email: str | None = None

    @field_validator("placeName", "location")
    @classmethod
    def _nonblank(cls, v: str) -> str:
        return _require_nonblank(v)

    @field_validator("placements")
    @classmethod
    def _nonempty(cls, v: list[str]) -> list[str]:
        labels = [s.strip() for s in v if isinstance(s, str) and s.strip()]
        if not labels:
            raise ValueError("at least one placement is required")
        return labels


class PlacementOut(BaseModel):
    label: str
    surfaceSlug: str
    qrToken: str
    url: str


class PlaceOut(BaseModel):
    slug: str
    placeName: str
    placeType: str | None
    location: str
    placements: list[PlacementOut]


class EventIn(BaseModel):
    qrToken: str
    kind: str

    @field_validator("kind")
    @classmethod
    def _known_kind(cls, v: str) -> str:
        if v not in EVENT_KINDS:
            raise ValueError(f"kind must be one of {sorted(EVENT_KINDS)}")
        return v


class BookingIn(BaseModel):
    qrToken: str
    experience: str
    gmv: float

    @field_validator("gmv")
    @classmethod
    def _positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("gmv must be positive")
        return v
