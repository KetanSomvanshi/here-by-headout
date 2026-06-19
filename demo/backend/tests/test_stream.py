"""Milestone 6 — the live booking ping. Replaces the fake setInterval loop with real SSE.

A reader subscribes to /stream on its own client; a booking POSTed on the main client
must arrive as an SSE data frame. Uses a second TestClient (separate transport, same app
+ DB override) so the streaming GET and the POST don't share one httpx client.
"""
import json
import threading
import time

import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.integration


def test_stream_is_event_stream(client):
    with client.stream("GET", "/stream") as resp:
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]


def test_booking_is_delivered_over_sse(client, tokens):
    received: dict = {}

    def reader():
        with TestClient(app).stream("GET", "/stream") as resp:
            for line in resp.iter_lines():
                if not line or not line.startswith("data:"):
                    continue
                payload = line[len("data:"):].strip()
                if not payload:
                    continue
                try:
                    data = json.loads(payload)
                except ValueError:
                    continue
                if "commission" in data:
                    received.update(data)
                    break

    t = threading.Thread(target=reader, daemon=True)
    t.start()
    time.sleep(0.3)  # let the subscriber attach before we publish

    client.post("/bookings", json={
        "qrToken": tokens["lobby-table-tent"],
        "experience": "Borghese Gallery",
        "gmv": 50.0,
    })

    t.join(timeout=5)
    assert received.get("experience") == "Borghese Gallery"
    assert received.get("commission") == 4.0
