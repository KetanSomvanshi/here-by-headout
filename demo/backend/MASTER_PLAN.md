# HERE by Headout — Backend Master Plan

> Hackathon (Hackin'26) backend for the partner onboarding flow.
> Goal: make every "live" claim in the designs literally true.
> Approach: **no Docker, no external services.** One Python process + a SQLite file.
> Build locally (`LOCAL_DEV.md`), then host (`HOSTING.md`) — same code, different env vars.

## 0. Project structure & fallback

The repo holds two independent things so the working prototype is always a safe fallback:

```
designs/          ← STATIC FALLBACK — original prototype, frozen, never touched by backend work
demo/             ← TARGET DEMO PROJECT (this plan)
  backend/        ← FastAPI app + these plan docs
  frontend/       ← a COPY of designs/, wired to the API (edit this, not designs/)
```

If the demo breaks, `designs/` still stands on its own. All backend wiring edits the
frontend **copy** under `demo/frontend/`.

## 1. Stack (locked)

| Layer | Choice |
|---|---|
| API + QR + tracking + analytics | **FastAPI** (Python 3.12, managed with `uv`) |
| Database | **SQLite** file via **SQLModel** (SQLAlchemy + Pydantic) |
| Live updates | **Server-Sent Events (SSE)** — in-process broadcaster, single worker |
| Auth | Skipped for the demo (simple email field; no password) |
| QR codes | `segno` |
| Posters | `Pillow` — overlay QR onto existing `frontend/assets/qr-asset-*.png` |
| Frontend | Static HTML in `demo/frontend/` (copy of `designs/`, served by FastAPI `StaticFiles`) |
| Host (demo) | **Local + Cloudflare Tunnel** (`cloudflared`) — phone scans hit your laptop |
| Host (durable) | **Fly.io** + a small volume for the SQLite file |

**Why no Docker / no Supabase:** the only thing Supabase was really buying us was
Realtime, and FastAPI does that natively with SSE. SQLite is a stdlib file — no DB
server, no container. The entire runtime dependency is "a box that runs one Python
process." Schema is structured so a later swap to Postgres is a connection-string change.

## 2. What the backend replaces

Today everything is faked client-side. The backend makes it real:

| Screen | Faked today | Backend job |
|---|---|---|
| `01-place-setup` | `sessionStorage` | Persist partner + place + placements |
| `02-generated-output` | static PNGs, `.txt` export | Real QR per placement → unique links; branded poster PNGs |
| QR scan | n/a | `/here/{token}` redirect that logs a scan (surface attribution) |
| guest storefront | static page | Co-branded page per place; log impressions/chats/recs |
| booking | random `setInterval` pings | Capture booking + commission, attributed to the QR surface; broadcast over SSE |
| `03-partner-dashboard` | hardcoded `surfaceData` | Aggregate funnel per surface; **live** via an SSE subscription |

## 3. Architecture

```
Guest scans QR ─► FastAPI  GET /here/{token}
                     ├─ INSERT events(kind='scan', placement_id)   # attribution
                     └─ 302 ─► guest storefront (static, co-branded by ?place=)
                                  ├─ POST /events  (impression|chat|rec)
                                  └─ books ─► POST /bookings
                                                ├─ INSERT bookings(commission, placement_id)
                                                └─ bus.publish(booking)  # in-process
                                                        │
Partner dashboard ◄── GET /stream  (Server-Sent Events) ◄┘   # live ping, no polling
Partner dashboard ◄── GET /analytics/{slug}                  # funnel aggregation
```

Single uvicorn worker → the SSE broadcaster is a plain in-process asyncio fan-out. No
Redis, no replication.

## 4. Data model (SQLite via SQLModel)

```python
Partner    (id, email, created_at)
Place      (id, partner_id, name, type, location, slug, created_at)
Placement  (id, place_id, label, surface_slug, qr_token unique, created_at)
Event      (id, placement_id, kind, created_at)        # impression|scan|chat|rec
Booking    (id, placement_id, experience, gmv, commission, created_at)
```

The dashboard funnel (impressions → scans → chats → recs → bookings → commission, per
surface) becomes a single `GROUP BY placement_id` over `events` + `bookings`. The
hardcoded `surfaceData` object in `03-partner-dashboard.html` collapses into one query.
`SQLModel.metadata.create_all()` builds the tables on startup — no migration tooling for
the hackathon (Alembic optional later).

## 5. API surface

| Method | Route | Purpose | Wires screen |
|---|---|---|---|
| `POST` | `/places` | Create place + placements, return slug + tokens | 01 |
| `GET` | `/places/{slug}` | Fetch place for storefront + dashboard | guest, 03 |
| `GET` | `/places/{slug}/posters` | Generate/return branded poster PNGs | 02 |
| `GET` | `/here/{token}` | Log scan, 302 → storefront | scan |
| `POST` | `/events` | Log impression/chat/rec from storefront | guest |
| `POST` | `/bookings` | Capture booking + commission, publish to SSE bus | booking |
| `GET` | `/stream` | **SSE** stream of live booking events | 03 |
| `GET` | `/analytics/{slug}` | Per-surface funnel + totals | 03 |

## 6. Build order (milestones)

All built and verified **locally** (`uv run uvicorn`) before any hosting. Each milestone
is **test-driven**: a matching group in `tests/` already encodes the contract (see
`TESTING.md`) — build until it goes green, run `uv run pytest` after each step.

1. **Scaffold** — FastAPI (`uv`), SQLModel + SQLite engine, `create_all` on startup,
   `/health`, `StaticFiles` serving `../frontend`, in-process event bus.
2. **Screen 01** — `POST /places`; replace `sessionStorage` write with an API call.
3. **Screen 02** — QR + poster generation; replace `.txt` export with real PNG downloads.
4. **Scan** — `/here/{token}` redirect + scan logging.
5. **Booking** — `POST /bookings` + commission attribution + `bus.publish`.
6. **Screen 03** — `GET /stream` (SSE) + `/analytics`; dashboard opens an `EventSource`
   for live pings (delete the fake `setInterval` loop).
7. **Seed + verify** — `app/seed.py` loads Casa Aurelia Rome + 4 placements + sample
   data on startup; verify the full scan→book→live-ping loop on localhost.
8. **Host** — Cloudflare Tunnel for the live phone demo, and/or Fly.io + volume for a
   durable URL. → `HOSTING.md`

## 7. Repo layout

```
demo/
  frontend/             # copy of designs/, wired to the API (served by StaticFiles)
  backend/
    MASTER_PLAN.md      # this file
    LOCAL_DEV.md        # local-first runbook (no Docker)
    HOSTING.md          # tunnel + Fly.io deploy
    TESTING.md          # test-driven spec + how to run the suite
    pyproject.toml      # uv-managed deps (+ [dev] = pytest/httpx)
    .env.example        # documented env vars
    fly.toml            # Fly.io config (durable host)
    Dockerfile          # build recipe for Fly only (NOT a local runtime dep)
    here.db             # SQLite file, created at runtime (gitignored)
    posters/            # generated poster PNGs (gitignored)
    app/
      main.py           # FastAPI app, CORS, StaticFiles (../frontend), startup create_all + seed
      config.py         # settings from env (.env locally); SEED_ON_STARTUP gate
      db.py             # SQLModel engine + get_session dependency (overridden in tests)
      models.py         # SQLModel tables (data model §4)
      utils.py          # slugify(), commission()  ← pure, unit-tested
      events_bus.py     # in-process asyncio fan-out for SSE
      seed.py           # demo data on startup
      routers/
        places.py
        tracking.py     # /here, /events
        bookings.py
        stream.py       # SSE endpoint
        analytics.py
      services/
        qr.py           # segno QR generation
        posters.py      # Pillow poster compositing
    tests/              # pytest suite — the executable contract (see TESTING.md)
      conftest.py       # in-memory DB + API-built fixtures
      test_*.py         # one group per milestone
      unit/test_helpers.py
```

## 8. Demo strategy

- Seed Casa Aurelia Rome + the 4 hotel placements from the design so the dashboard opens
  populated.
- Run locally, expose with Cloudflare Tunnel so QR links resolve from a phone.
- Live loop for judges: scan a real QR with a phone → storefront opens → tap book →
  the dashboard ping fires over SSE with no refresh. That single loop is the pitch.

## 9. What I need from you

**To build locally (now):** Python 3.12 + `uv`. Nothing else — no Docker, no accounts,
no DB server. SQLite file is created automatically.

**To host (later):**
- Live phone demo: install `cloudflared` (`brew install cloudflared`).
- Durable URL: a free Fly.io account (`! open https://fly.io`).
