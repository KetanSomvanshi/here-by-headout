"""Shared fixtures.

Tests run hermetically: an in-memory SQLite DB per test (no file, no Docker) and the
startup seed disabled. Data is created through the public API so tests assert the real
end-to-end contract rather than internals. See TESTING.md.
"""
import os

# Must be set before `app` is imported so startup honors them.
os.environ.setdefault("SEED_ON_STARTUP", "0")
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("APP_BASE_URL", "http://testserver")

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.db import get_session


@pytest.fixture(name="session")
def session_fixture():
    """A fresh in-memory DB shared across one test via a single connection."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    """TestClient with the DB dependency pointed at the in-memory session."""
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


# ── domain fixtures (created via the public API) ──

SETUP = {
    "placeName": "Casa Aurelia Rome",
    "placeType": "Hotel",
    "location": "Via Germanico, Prati, Rome",
    "placements": ["Lobby table-tent", "Guest room card", "Breakfast counter", "Elevator"],
    "email": "host@example.com",
}


@pytest.fixture
def place(client):
    """Create a place and return its API response body (slug + placements with tokens)."""
    resp = client.post("/places", json=SETUP)
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.fixture
def tokens(place):
    """Map surfaceSlug -> qrToken for the created place."""
    return {p["surfaceSlug"]: p["qrToken"] for p in place["placements"]}
