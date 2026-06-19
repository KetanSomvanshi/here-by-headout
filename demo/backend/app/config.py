"""App settings, loaded from environment (and a local .env if present).

Sensible local defaults are baked in so the app runs with zero config. Hosting is a
cutover that changes only these env vars, not code (see HOSTING.md).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # SQLite file locally; on Fly this points at the mounted volume.
    database_url: str = "sqlite:///./here.db"
    # QR posters encode {app_base_url}/here/{token}. Set to the public URL when hosted.
    app_base_url: str = "http://localhost:8000"
    # Comma-separated list of allowed CORS origins.
    cors_origins: str = "http://localhost:8000"
    # Load demo data on startup. Tests set this to 0 so seed data never bleeds in.
    seed_on_startup: bool = True
    # Seconds an idle /stream connection stays open before closing. The browser's
    # EventSource then auto-reconnects (see the `retry:` hint), so the dashboard stays
    # live. A bounded lifetime is also what lets the test harness — whose TestClient
    # buffers the whole response — ever return. See app/routers/stream.py.
    sse_idle_timeout: float = 3.0

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
