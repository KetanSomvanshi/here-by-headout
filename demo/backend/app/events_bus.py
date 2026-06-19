"""In-process asyncio fan-out for SSE.

Single uvicorn worker → "live" needs no Redis. Each /stream connection registers a queue
*together with the event loop it lives on*. publish() wakes every subscriber on its own
loop via call_soon_threadsafe — necessary because sync FastAPI handlers (and the test's
second client) publish from a different thread/loop than the one the queue waits on.
See MASTER_PLAN.md §3.
"""
import asyncio


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[asyncio.Queue, asyncio.AbstractEventLoop] = {}

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._subscribers[q] = asyncio.get_running_loop()
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        self._subscribers.pop(q, None)

    def publish(self, payload: dict) -> None:
        """Fan a payload out to all subscribers, each on the loop that owns its queue."""
        for q, loop in list(self._subscribers.items()):
            loop.call_soon_threadsafe(q.put_nowait, payload)


bus = EventBus()
