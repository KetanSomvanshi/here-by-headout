"""SQLModel engine + the get_session dependency (overridden by tests)."""
from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

# check_same_thread=False so the SSE endpoint and request handlers can share a
# file-backed SQLite connection across threads. Tests override get_session entirely.
_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=_connect_args)


def init_db() -> None:
    """Create all tables. Models must be imported before this runs."""
    import app.models  # noqa: F401  (register tables on the metadata)

    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """FastAPI dependency yielding a DB session. Tests override this."""
    with Session(engine) as session:
        yield session
