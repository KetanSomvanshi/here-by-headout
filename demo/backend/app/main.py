"""FastAPI app: CORS, routers, static frontend, startup create_all + optional seed."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.db import init_db
from app.routers import analytics, bookings, places, posters, stream, tracking

_FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if settings.seed_on_startup:
        from app.seed import seed

        seed()
    yield


app = FastAPI(title="HERE by Headout", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(places.router)
app.include_router(posters.router)
app.include_router(tracking.router)
app.include_router(bookings.router)
app.include_router(stream.router)
app.include_router(analytics.router)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}


# Static frontend last so API routes take precedence. html=True serves index.html.
if _FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=_FRONTEND_DIR, html=True), name="frontend")
