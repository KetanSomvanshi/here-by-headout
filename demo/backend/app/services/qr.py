"""QR generation with segno. A QR encodes {APP_BASE_URL}/here/{qr_token}."""
import io

import segno

from app.config import settings


def here_url(qr_token: str) -> str:
    return f"{settings.app_base_url}/here/{qr_token}"


def qr_png_bytes(qr_token: str, scale: int = 10, border: int = 2) -> bytes:
    """A high error-correction QR as PNG bytes (so it survives compositing/print)."""
    qr = segno.make(here_url(qr_token), error="h")
    buf = io.BytesIO()
    qr.save(buf, kind="png", scale=scale, border=border, dark="#1a0a2e", light="#ffffff")
    return buf.getvalue()
