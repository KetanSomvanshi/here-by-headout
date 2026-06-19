"""Live booking pings over Server-Sent Events. Replaces the prototype's fake loop.

The generator yields a booking frame as soon as one is published, and closes after
`SSE_IDLE_TIMEOUT` seconds of silence. The browser's EventSource auto-reconnects (we send
a short `retry:` hint), so the dashboard stays continuously live. The bounded lifetime is
also what makes this testable: the installed Starlette TestClient buffers the whole
response, so an unbounded stream would deadlock the test (see app/events_bus.py).
"""
import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.config import settings
from app.events_bus import bus

router = APIRouter(tags=["stream"])


@router.get("/stream")
async def stream() -> StreamingResponse:
    queue = bus.subscribe()

    async def event_source():
        yield "retry: 1000\n\n"   # reconnect quickly so live gaps stay tiny
        yield ": connected\n\n"   # flush headers immediately
        try:
            while True:
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=settings.sse_idle_timeout)
                    yield f"data: {json.dumps(payload)}\n\n"
                except asyncio.TimeoutError:
                    break  # idle → close; client reconnects
        finally:
            bus.unsubscribe(queue)

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
