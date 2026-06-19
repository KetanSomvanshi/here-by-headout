"""Branded poster compositing with Pillow.

Each placement gets a real QR composited onto one of the existing poster artworks
(frontend/assets/qr-asset-*.png, 524×924). A white rounded card hosts the QR so it stays
scannable on any artwork. Posters are generated on demand and cached in posters/.
"""
import io
from pathlib import Path

from PIL import Image, ImageDraw

from app.services.qr import qr_png_bytes

_BACKEND_DIR = Path(__file__).resolve().parents[2]
_ARTWORK_DIR = _BACKEND_DIR.parent / "frontend" / "assets"
POSTERS_DIR = _BACKEND_DIR / "posters"

# The four artworks cycle across a place's placements so each poster looks distinct.
_ARTWORKS = ["qr-asset-rome.png", "qr-asset-stay.png", "qr-asset-ticket.png", "qr-asset-polaroid.png"]


def _artwork_for(index: int) -> Image.Image:
    name = _ARTWORKS[index % len(_ARTWORKS)]
    path = _ARTWORK_DIR / name
    if path.exists():
        return Image.open(path).convert("RGBA")
    # Fallback so posters still render if artwork is missing (e.g. on a fresh host).
    return Image.new("RGBA", (524, 924), (122, 0, 240, 255))


def build_poster_png(qr_token: str, index: int = 0) -> bytes:
    """Composite a QR onto poster artwork and return PNG bytes."""
    poster = _artwork_for(index)
    w, h = poster.size

    # White rounded card centered horizontally in the lower third.
    card = int(w * 0.46)
    cx = (w - card) // 2
    cy = int(h * 0.60)
    draw = ImageDraw.Draw(poster)
    draw.rounded_rectangle(
        [cx - 16, cy - 16, cx + card + 16, cy + card + 16],
        radius=24,
        fill=(255, 255, 255, 255),
    )

    qr_img = Image.open(io.BytesIO(qr_png_bytes(qr_token))).convert("RGBA")
    qr_img = qr_img.resize((card, card), Image.NEAREST)
    poster.alpha_composite(qr_img, (cx, cy))

    out = io.BytesIO()
    poster.save(out, format="PNG")
    return out.getvalue()
