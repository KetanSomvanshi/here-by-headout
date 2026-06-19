# HERE by Headout — Local Development

Build and run the **entire** stack on your laptop with **no Docker and no external
services**. The whole thing is one Python process plus a SQLite file. Hosting later is a
cutover that changes only env vars, not code.

> This is the **demo project** under `demo/`. The original static prototype stays frozen
> at the repo root in `designs/` as a fallback. All wiring here edits the frontend copy
> in `demo/frontend/`, never `designs/`.

## Why this is so light

- **SQLite** is a file in the repo — no database server, no container.
- **Live updates** are Server-Sent Events served by FastAPI itself — no Supabase, no
  Redis. A single uvicorn worker broadcasts booking events in-process.
- **Posters** are PNGs written to `posters/` and served as static files.

```
Laptop                                  Phone / browser
┌──────────────────────────────┐
│ uvicorn app.main:app :8000    │◄──── browser: dashboard EventSource /stream
│  FastAPI                       │◄──── phone: scans QR → /here/{token}
│   - /places /bookings          │
│   - /here redirect + tracking  │
│   - /stream (SSE live pings)   │
│   - /analytics                 │
│   - StaticFiles → ../frontend  │
│  SQLite: here.db (file)        │
│  posters/*.png                 │
└──────────────────────────────┘
```

## Prerequisites

| Tool | Why | Install |
|---|---|---|
| **Python 3.12** | FastAPI runtime | `brew install python@3.12` |
| **uv** | dependency + venv manager | `brew install uv` |
| **cloudflared** *(optional)* | expose localhost so a phone can scan QR | `brew install cloudflared` |

No Docker. No DB server. No cloud account.

## Setup & run

```bash
cd demo/backend

# 1. install deps (creates .venv from pyproject.toml)
uv sync

# 2. run — SQLite file + tables are created and seeded automatically on startup
uv run uvicorn app.main:app --reload --port 8000
```

That's it. On first start the app calls `SQLModel.metadata.create_all()` and
`app/seed.py` loads demo data (Casa Aurelia Rome + 4 placements + sample events/bookings)
so the dashboard opens populated.

Open (frontend is `demo/frontend/`, mounted at the site root by StaticFiles):
```bash
open http://localhost:8000/partner-flow/00-landing.html   # frontend
open http://localhost:8000/docs                           # API docs
```

## Environment (`.env`)

Optional locally — sensible defaults are baked in. Override only if needed:

```
DATABASE_URL=sqlite:///./here.db
APP_BASE_URL=http://localhost:8000     # QR links point here
CORS_ORIGINS=http://localhost:8000
```

## Reset the database

SQLite is just a file, so a clean slate is:

```bash
rm here.db        # next startup recreates + reseeds
```

(For a fresh demo right before judging, delete it so numbers start from the seed.)

## Test the full loop locally

1. **Setup** — `POST /places` from screen 01 → a `places` row is created.
2. **QR kit** — `GET /places/{slug}/posters` → real poster PNGs download.
3. **Scan** — open a poster's `/here/{token}` URL → 302 to storefront; an `events`
   `scan` row is logged.
4. **Book** — `POST /bookings` → a `bookings` row with commission.
5. **Live** — keep screen 03 open (it holds an `EventSource` to `/stream`); the booking
   pushes through SSE and the dashboard ping fires with no refresh.

If step 5 works on localhost, it works hosted unchanged.

## Live phone demo from your laptop (Cloudflare Tunnel)

To let a real phone scan a QR that hits your local server:

```bash
# terminal 1
uv run uvicorn app.main:app --port 8000
# terminal 2
cloudflared tunnel --url http://localhost:8000
# prints a public https URL, e.g. https://random-words.trycloudflare.com
```

Set `APP_BASE_URL` to that tunnel URL and restart so generated QR codes encode the
public address. Now scanning from a phone reaches your laptop — zero hosting needed.

## Day-to-day loop

```bash
uv run uvicorn app.main:app --reload --port 8000   # hot reload on code edits
# edit models → rm here.db to rebuild schema (hackathon: no migrations)
```

## Cutover to hosted (later — no code changes)

Same app, durable URL on Fly.io with a volume for the SQLite file. Only env vars change
(`DATABASE_URL` → the volume path, `APP_BASE_URL` → the Fly URL). See `HOSTING.md`.
