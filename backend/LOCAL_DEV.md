# HERE by Headout — Local Development

Build and run the **entire** stack on your laptop first — Postgres, Auth, Realtime,
Storage, and the FastAPI API — with **zero cloud dependency**. Hosting is a later
cutover that changes only env vars, not code.

## Why local-first works cleanly here

The Supabase **CLI** runs the full Supabase stack in Docker locally (`supabase start`):
the same Postgres, Auth, Realtime, and Storage you'll use in the cloud. So "local" and
"hosted" are the *same software* — going live later is `supabase link` + `db push` +
deploy FastAPI. Nothing in the app code changes; only `.env` points at a different host.

```
Laptop (Docker)                          FastAPI (uvicorn --reload)
┌─────────────────────────────┐          ┌────────────────────────────┐
│ supabase start               │◄────────►│ app.main:app  :8000        │
│  Postgres   :54322           │ wire+REST│  - /here redirect+tracking │
│  Auth/Realtime/Storage:54321 │◄─────────│  - /places /bookings       │
│  Studio UI  :54323           │ browser  │  - /analytics              │
└─────────────────────────────┘ realtime │  - StaticFiles → ../designs│
        ▲                                 └────────────────────────────┘
        └── browser subscribes to Realtime at localhost:54321
```

## Prerequisites

| Tool | Why | Install |
|---|---|---|
| **Python 3.12** | FastAPI runtime | `brew install python@3.12` |
| **uv** | dependency + venv manager | `brew install uv` |
| **Docker Desktop** | runs the local Supabase stack | `brew install --cask docker` |
| **Supabase CLI** | spins up local Postgres/Auth/Realtime/Storage | `brew install supabase/tap/supabase` |

No cloud account needed to start building.

## One-time setup

```bash
cd backend

# 1. Python deps (creates .venv, installs from pyproject.toml)
uv sync

# 2. Initialize + start the local Supabase stack (Docker)
supabase init          # creates supabase/ config (first time only)
supabase start         # boots Postgres + Auth + Realtime + Storage + Studio
                       # prints local URL + anon key + service_role key

# 3. Apply schema + seed
supabase db reset      # runs migrations in supabase/migrations + seed.sql
```

`supabase start` prints something like:

```
API URL:        http://localhost:54321
DB URL:         postgresql://postgres:postgres@localhost:54322/postgres
Studio URL:     http://localhost:54323
anon key:       eyJ...
service_role:   eyJ...
```

Copy those into `.env.local` (see below). The keys are deterministic for local dev, so
they're safe to commit to `.env.example` if we want.

## Environment (`.env.local`)

```
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=<printed by supabase start>
SUPABASE_SERVICE_KEY=<printed by supabase start>
APP_BASE_URL=http://localhost:8000        # QR links point here locally
CORS_ORIGINS=http://localhost:8000
```

## Run the app

```bash
# terminal 1: local data plane (leave running)
supabase start

# terminal 2: FastAPI with hot reload
uv run uvicorn app.main:app --reload --port 8000

# open the frontend (served by FastAPI StaticFiles)
open http://localhost:8000/designs/partner-flow/00-landing.html
# API docs
open http://localhost:8000/docs
# local DB browser
open http://localhost:54323
```

## Schema as migrations (not ad-hoc SQL)

So local and cloud stay identical, manage DDL as Supabase migrations:

```bash
supabase migration new init_schema     # creates a timestamped .sql file
# paste tables into it (the data model from MASTER_PLAN §4)
supabase migration new rls_policies
supabase db reset                       # re-applies all migrations + seed locally
```

`supabase/seed.sql` holds the demo data (Casa Aurelia Rome + 4 placements + sample
events/bookings) so the dashboard opens populated every `db reset`.

## Test the full loop locally

1. **Setup** — `POST /places` from screen 01 → row appears in Studio (`places`).
2. **QR kit** — `GET /places/{slug}/posters` → real poster PNGs download.
3. **Scan** — open a poster's `/here/{token}` URL → 302 to storefront, `events`
   gets a `scan` row.
4. **Book** — `POST /bookings` → `bookings` row with commission.
5. **Live** — keep screen 03 open; the booking insert pushes through **local**
   Realtime and the dashboard ping fires with no refresh.

If step 5 works on localhost, it works in production unchanged.

## Day-to-day loop

```bash
supabase start                  # once per session
uv run uvicorn app.main:app --reload --port 8000
# edit code → uvicorn reloads; edit schema → supabase db reset
supabase stop                   # frees Docker when done (data persists)
```

## Cutover to hosted (later — no code changes)

1. Create the cloud project: `supabase login && supabase link --project-ref <ref>`
2. Push the same migrations up: `supabase db push`
3. Load seed in the cloud SQL editor (or `supabase db push --include-seed`).
4. Deploy FastAPI to Render (see `HOSTING.md`); set the cloud `.env` values.
5. Set `APP_BASE_URL` to the Render URL so freshly generated QR links point at prod.

Everything you built and tested locally runs as-is — only the four env vars differ.
