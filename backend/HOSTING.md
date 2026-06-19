# HERE by Headout — Hosting Plan

Everything runs on free managed tiers. Two providers: **Supabase** (data plane) and
**Render** (FastAPI). Static frontend is served by FastAPI, or split onto Cloudflare
Pages if we want it on its own domain.

## Topology

```
                 ┌────────────────────────────┐
   Phone (QR) ──►│  Render: FastAPI service     │
   Browser    ──►│  - /here redirect + tracking │
                 │  - /places, /bookings        │
                 │  - /analytics                │
                 │  - StaticFiles → designs/    │
                 └──────────────┬───────────────┘
                                │ Postgres wire + REST
                 ┌──────────────▼───────────────┐
                 │  Supabase                     │
                 │  - Postgres (data model)      │
                 │  - Auth (magic link)          │
                 │  - Realtime (bookings stream) │◄── browser subscribes directly
                 │  - Storage (poster PNGs)      │
                 └──────────────────────────────┘
```

## Provider choices & rationale

| Need | Provider | Free tier reality |
|---|---|---|
| FastAPI host | **Render** | Free web service; sleeps after 15 min idle (fine for demo; ping to keep warm before judging) |
| Postgres + auth + realtime + storage | **Supabase** | 500MB DB, 50k MAU auth, realtime + storage included |
| Static assets / CDN (optional) | **Cloudflare Pages** | Only if we want the marketing pages on a custom domain separate from the API |

**Alternatives if Render's cold start annoys us:** Fly.io (always-on small VM, free
allowance) or Railway (no sleep, usage-based). Swap is a one-file change — same
`uvicorn` command.

## Environment variables

```
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_ANON_KEY=...        # safe for browser (Realtime subscribe)
SUPABASE_SERVICE_KEY=...     # server-only, never shipped to browser
APP_BASE_URL=https://<service>.onrender.com   # used to build QR short links
CORS_ORIGINS=https://<service>.onrender.com
```

## Deploy steps

### Supabase (one-time)
1. Create project at dashboard → copy URL + anon + service keys.
2. Run `sql/schema.sql`, `sql/policies.sql`, `sql/seed.sql` in the SQL editor.
3. Enable Realtime on the `bookings` table (Database → Replication).

### Render (FastAPI)
1. Connect the GitHub repo, root = `backend/`.
2. `render.yaml` defines the service:
   ```yaml
   services:
     - type: web
       name: here-api
       env: python
       buildCommand: "pip install uv && uv sync"
       startCommand: "uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT"
       envVars:
         - key: SUPABASE_URL
           sync: false
         - key: SUPABASE_ANON_KEY
           sync: false
         - key: SUPABASE_SERVICE_KEY
           sync: false
   ```
3. Add the env vars in the Render dashboard (mark service key as secret).
4. Deploy. `APP_BASE_URL` = the assigned `*.onrender.com` URL → set it, redeploy so QR
   links point at the live host.

## QR links in production

QR posters encode `https://<APP_BASE_URL>/here/{qr_token}`. The redirect logs the scan
and 302s to the storefront. Because the token is per-placement, attribution is baked
into the URL — no cookies, no integration, matching the design's promise.

## Cost

$0 for the hackathon. If it graduates: Render paid ($7/mo always-on) + Supabase Pro
($25/mo) covers real traffic, but that's a post-hackathon decision.

## Pre-demo checklist

- [ ] Seed data loaded so dashboard opens populated
- [ ] Render service pinged warm (no cold start during the pitch)
- [ ] One physical QR poster printed/on-screen to scan live
- [ ] Realtime confirmed: scan → book → dashboard ping with no refresh
