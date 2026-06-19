# HERE by Headout — Test-Driven Spec & Testing Setup

These tests are the **executable contract**. They encode every behavior the static
prototype currently fakes, so when you build the real backend you can prove parity:
each milestone in `MASTER_PLAN.md §6` turns a test group from red to green.

> Write code until the tests pass. Don't change a test to match the code unless the
> contract itself is wrong.

## How to run

```bash
cd demo/backend
uv sync --extra dev          # installs pytest + httpx
uv run pytest                # whole suite
uv run pytest -q tests/test_places.py   # one group
uv run pytest -m unit        # just the pure-function unit tests
```

Until `app/` is scaffolded, collection fails on `import app` — that's expected for TDD.
Milestone 1 (scaffold) makes the suite collect; later milestones turn groups green.

## Test → milestone → mocked-behavior map

| Test file | Milestone | Replaces this mock in the prototype |
|---|---|---|
| `tests/unit/test_helpers.py` | 1 | `slugify()` and the `commission = gmv*0.08` math in 02/03 |
| `tests/test_health.py` | 1 | n/a (smoke) |
| `tests/test_places.py` | 2 | `sessionStorage` setup + validation in `01-place-setup.html` |
| `tests/test_posters.py` | 3 | static PNGs + `.txt` export + unique link per spot in `02` |
| `tests/test_tracking.py` | 4 | the `/here/{slug}?surface=` scan link; storefront event logging |
| `tests/test_bookings.py` | 5 | random `setInterval` booking pings; commission attribution |
| `tests/test_stream.py` | 6 | the fake live "Booking just landed" ping loop (now real SSE) |
| `tests/test_analytics.py` | 6 | the hardcoded `surfaceData` funnel + per-surface breakdown in `03` |

## API contract the tests assert

All request/response bodies are JSON unless noted. Request keys are **camelCase** to match
the prototype's existing JS (minimal frontend rewrite).

### `POST /places` → 201
```jsonc
// request
{ "placeName": "Casa Aurelia Rome", "placeType": "Hotel",
  "location": "Via Germanico, Prati, Rome",
  "placements": ["Lobby table-tent", "Guest room card", "Breakfast counter", "Elevator"],
  "email": "host@example.com" }            // optional
// response
{ "slug": "casa-aurelia-rome",
  "placeName": "...", "placeType": "...", "location": "...",
  "placements": [
    { "label": "Lobby table-tent", "surfaceSlug": "lobby-table-tent",
      "qrToken": "<unique>", "url": "<APP_BASE_URL>/here/<qrToken>" }
  ] }
```
- 422 when `placeName` is blank, `location` is blank, or `placements` is empty.
- Every `qrToken` is unique across all placements.

### `GET /places/{slug}` → 200 / 404
Returns the place + placements (same shape as above). 404 for unknown slug.

### `GET /places/{slug}/posters` → 200
`{ "posters": [ { "placement", "surfaceSlug", "qrToken", "png": "/places/{slug}/posters/{surfaceSlug}.png" } ] }`
- One poster per placement (count parity with setup).

### `GET /places/{slug}/posters/{surfaceSlug}.png` → 200
`Content-Type: image/png`, non-empty body (real QR composited onto artwork).

### `GET /here/{qrToken}` → 302
- `Location` contains the place slug **and** the surface, e.g.
  `/guest-flow/01-map-storefront.html?place=casa-aurelia-rome&surface=lobby-table-tent`.
- Logs one `scan` event for that placement. 404 for unknown token.

### `POST /events` → 201
`{ "qrToken": "...", "kind": "impression" | "chat" | "rec" }`
- 422 for an unknown `kind`; 404 for an unknown token.

### `POST /bookings` → 201
```jsonc
{ "qrToken": "...", "experience": "Vatican Museums", "gmv": 38.00 }
// response
{ "id": "...", "experience": "Vatican Museums", "gmv": 38.0,
  "commission": 3.04,                       // round(gmv * 0.08, 2)
  "placement": { "surfaceSlug": "lobby-table-tent", "label": "Lobby table-tent" } }
```
- `commission == round(gmv * 0.08, 2)`. 422 for `gmv <= 0`; 404 for unknown token.
- Publishes the booking to the in-process SSE bus.

### `GET /stream` → 200 `text/event-stream`
- After a `POST /bookings`, a connected client receives an SSE `data:` frame whose JSON
  carries at least `experience` and `commission`.

### `GET /analytics/{slug}` → 200
```jsonc
{ "place": { "slug": "...", "placeName": "..." },
  "totals": { "impressions": int, "scans": int, "chats": int, "recs": int,
              "bookings": int, "commission": float, "gmv": float, "conversion": float },
  "surfaces": [ { "surfaceSlug", "label", "impressions", "scans", "chats", "recs",
                  "bookings", "commission", "gmv" } ] }
```
- `totals` are exact sums over logged events + bookings.
- `commission == round(gmv * 0.08, 2)`; `conversion == round(bookings / scans, 4)` (0 if no scans).
- One `surfaces` entry per placement; per-surface counts sum to `totals`.

## Testability requirements the app must honor

So tests run hermetically (no file DB, no demo seed bleeding into assertions):

- `app.db` exposes a `get_session` FastAPI dependency that tests override with an
  in-memory SQLite session.
- Startup seeding is gated by env: `SEED_ON_STARTUP=0` disables `app/seed.py`.
- `commission()` and `slugify()` live in `app/utils.py` as importable pure functions.

## Philosophy

- **Black-box first.** Tests create data through the public API (`POST /places`,
  `/here`, `/events`, `/bookings`) and assert through `/analytics` — so they survive
  internal refactors and prove the *real* end-to-end loop, not implementation details.
- **Pin the numbers.** The funnel/commission assertions reproduce the prototype's own
  math, so "the demo still works" is a checkable fact, not a vibe.
- **Fast.** In-memory SQLite, one process, no Docker — the whole suite runs in seconds.
