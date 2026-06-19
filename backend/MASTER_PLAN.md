# HERE by Headout — Backend Master Plan

> Hackathon (Hackin'26) backend for the partner onboarding flow.
> Goal: make every "live" claim in the designs literally true, hosted entirely on free tiers.

## 1. Stack (locked)

| Layer | Choice |
|---|---|
| API + QR + tracking + analytics | **FastAPI** (Python 3.12, managed with `uv`) |
| Database | **Supabase Postgres** |
| Live updates | **Supabase Realtime** — browser subscribes directly to `bookings` inserts |
| Auth | **Supabase Auth** (magic link, passwordless) |
| QR codes | `segno` (SVG/PNG QR) |
| Posters | `Pillow` — overlay QR onto existing artwork in `designs/assets/qr-asset-*.png` |
| Frontend | Existing static HTML in `designs/` (served by FastAPI `StaticFiles` or Cloudflare Pages) |
| Hosting | **Render** (FastAPI) + **Supabase** (DB/auth/realtime/storage) |

**Why Supabase behind a Python backend:** it removes the two hardest hackathon problems —
auth and realtime — so FastAPI owns only the interesting work: QR generation, scan
attribution, booking capture, and analytics aggregation. The dashboard's live booking
pings come from the browser subscribing to Supabase Realtime directly; FastAPI just
writes rows to the same Postgres.

## 2. What the backend replaces

Today everything is faked client-side. The backend makes it real:

| Screen | Faked today | Backend job |
|---|---|---|
| `01-place-setup` | `sessionStorage` | Persist partner + place + placements; magic-link auth |
| `02-generated-output` | static PNGs, `.txt` export | Real QR per placement → unique short links; branded poster PNGs |
| QR scan | n/a | `/here/{token}` redirect that logs a scan (surface attribution) |
| guest storefront | static page | Co-branded page per place; log impressions/chats/recs |
| booking | random `setInterval` pings | Capture booking + commission, attributed to the QR surface |
| `03-partner-dashboard` | hardcoded `surfaceData` | Aggregate funnel per surface, **live** via Realtime |

## 3. Architecture

```
Guest scans QR ─► FastAPI  GET /here/{token}
                     ├─ INSERT events(kind='scan', placement_id)   # attribution
                     └─ 302 ─► guest storefront (static, co-branded by ?place=)
                                  └─ books ─► FastAPI POST /bookings
                                                └─ INSERT bookings(commission, placement_id)
                                                        │
Partner dashboard ◄── Supabase Realtime (websocket on bookings) ◄──┘   # live ping, no polling
Partner dashboard ◄── FastAPI GET /analytics/{place_slug}              # funnel aggregation
```

## 4. Data model (Postgres)

```sql
partners    (id uuid pk, email text unique, created_at timestamptz)
places      (id uuid pk, partner_id fk, name text, type text, location text,
             slug text unique, created_at timestamptz)
placements  (id uuid pk, place_id fk, label text, surface_slug text,
             qr_token text unique, created_at timestamptz)
events      (id uuid pk, placement_id fk, kind text,   -- impression|scan|chat|rec
             created_at timestamptz)
bookings    (id uuid pk, placement_id fk, experience text,
             gmv numeric, commission numeric, created_at timestamptz)
```

The dashboard funnel (impressions → scans → chats → recs → bookings → commission, per
surface) becomes a single `GROUP BY placement_id` over `events` + `bookings`. The
hardcoded `surfaceData` object in `03-partner-dashboard.html` collapses into one query.

## 5. API surface

| Method | Route | Purpose | Wires screen |
|---|---|---|---|
| `POST` | `/places` | Create place + placements, return slug + tokens | 01 |
| `GET` | `/places/{slug}` | Fetch place for storefront + dashboard | guest, 03 |
| `GET` | `/places/{slug}/posters` | Generate/return branded poster PNGs (zip or per-spot) | 02 |
| `GET` | `/here/{token}` | Log scan, 302 → storefront | scan |
| `POST` | `/events` | Log impression/chat/rec from storefront | guest |
| `POST` | `/bookings` | Capture booking + commission | booking |
| `GET` | `/analytics/{slug}` | Per-surface funnel + totals | 03 |
| `POST` | `/auth/magic-link` | (Supabase) partner login | 01 |

## 6. Build order (milestones)

1. **Infra** — Supabase project, schema SQL, RLS policies.
2. **Scaffold** — FastAPI app (`uv`), routers, Supabase client, Render config, `/health`.
3. **Screen 01** — `POST /places`; replace `sessionStorage` write with an API call.
4. **Screen 02** — QR + poster generation; replace `.txt` export with real PNG downloads.
5. **Scan** — `/here/{token}` redirect + scan logging.
6. **Booking** — `POST /bookings` + commission attribution.
7. **Screen 03** — `/analytics` aggregation + browser Supabase Realtime subscription
   (delete the fake `setInterval` ping loop).
8. **Polish** — seed demo data so the dashboard looks alive on first load for judges.

## 7. Proposed repo layout

```
backend/
  MASTER_PLAN.md        # this file
  HOSTING.md            # deploy runbook
  pyproject.toml        # uv-managed deps
  .env.example          # SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_ANON_KEY
  render.yaml           # Render deploy config
  app/
    main.py             # FastAPI app, CORS, StaticFiles for designs/
    config.py           # settings from env
    db.py               # Supabase client
    routers/
      places.py
      tracking.py       # /here, /events
      bookings.py
      analytics.py
    services/
      qr.py             # segno QR generation
      posters.py        # Pillow poster compositing
  sql/
    schema.sql          # tables
    policies.sql        # RLS
    seed.sql            # demo data for judging
```

## 8. Demo strategy (so it lands with judges)

- Seed one place ("Casa Aurelia Rome") with the 4 hotel placements already in the design.
- Pre-load realistic events/bookings so the dashboard opens populated.
- During the demo: scan a real QR with a phone → storefront opens → tap "book" →
  watch the booking ping appear on the dashboard **live** via Realtime. That single
  loop is the whole pitch.

## 9. What I need from you (interactive)

1. Create a Supabase project: `! open https://supabase.com/dashboard`
2. Paste back: project URL, `anon` key, `service_role` key → I'll put them in `.env`.
3. A Render account (free) when we're ready to deploy: `! open https://render.com`
