# HERE by Headout — Hosting Plan

The app is one Python process + a SQLite file + SSE. That shapes everything: you need a
host that runs a **persistent process** (for SSE) and gives the SQLite file a
**persistent disk**. Two recommended paths:

- **A. Cloudflare Tunnel** — zero hosting, for the live judged demo.
- **B. Fly.io + volume** — a real durable URL.

## Why not serverless / edge

Vercel, Netlify functions, and Cloudflare Workers **buffer or time out streaming
responses** (SSE needs a long-lived connection) and have **no persistent local
filesystem** for `here.db`. They're the wrong shape for this app. Pick a platform that
runs a normal long-running process.

---

## Path A — Cloudflare Tunnel (demo, $0, nothing to deploy)

Run the app on your laptop and expose it publicly so a phone can scan the QR.

```bash
# terminal 1
uv run uvicorn app.main:app --port 8000
# terminal 2
cloudflared tunnel --url http://localhost:8000
# → https://<random>.trycloudflare.com
```

1. Set `APP_BASE_URL=https://<random>.trycloudflare.com` and restart so QR codes encode
   the public URL.
2. Scan from a phone → it reaches your laptop. Data lives in your local `here.db`.

Best for the actual pitch: simplest possible, full control, no cold starts, and you can
`rm here.db` for a clean run right before judging.

---

## Path B — Fly.io (durable URL with persistent SQLite)

Always-on small VM, free allowance, and a volume so the database survives restarts.

### Build context (because frontend & backend are separate paths)

The app serves `demo/frontend/` via StaticFiles, which lives **outside** `demo/backend/`.
So the Docker build context is **`demo/`** (the parent), not `demo/backend/`. Put both
`Dockerfile` and `fly.toml` at `demo/` so the image includes `frontend/` and `backend/`.

`demo/Dockerfile` (build recipe Fly uses — **not** a local runtime dependency):
```dockerfile
FROM python:3.12-slim
RUN pip install uv
WORKDIR /app
COPY backend/pyproject.toml backend/uv.lock ./backend/
RUN cd backend && uv sync --frozen --no-dev
COPY backend/ ./backend/
COPY frontend/ ./frontend/         # StaticFiles serves ../frontend relative to backend
WORKDIR /app/backend
CMD ["uv","run","uvicorn","app.main:app","--host","0.0.0.0","--port","8080"]
```

`demo/fly.toml`:
```toml
app = "here-by-headout"
primary_region = "fra"

[build]

[env]
  DATABASE_URL = "sqlite:////data/here.db"   # on the mounted volume
  CORS_ORIGINS = "https://here-by-headout.fly.dev"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = false   # keep alive so SSE connections persist
  min_machines_running = 1

[mounts]
  source = "here_data"
  destination = "/data"
```

### Deploy

```bash
cd demo                         # build context = demo/ (includes frontend/ + backend/)
fly launch --no-deploy          # creates the app (reuse the fly.toml above)
fly volumes create here_data --size 1 --region fra
fly secrets set APP_BASE_URL=https://here-by-headout.fly.dev
fly deploy
```

Run a **single machine / one worker** so the in-process SSE bus reaches every dashboard
client. (Multiple machines would need a shared bus, e.g. Redis — out of scope for the
hackathon.)

### Notes
- The SQLite file lives at `/data/here.db` on the volume → survives deploys and restarts.
- `auto_stop_machines = false` keeps the process warm so SSE streams aren't dropped.
- Seed runs on startup; to reseed, `fly ssh console` and `rm /data/here.db`, then restart.

---

## Environment variables

```
DATABASE_URL     sqlite:///./here.db          (local)  |  sqlite:////data/here.db (Fly)
APP_BASE_URL     http://localhost:8000        (local)  |  https://<app>.fly.dev   (Fly)
                 https://<x>.trycloudflare.com (tunnel)
CORS_ORIGINS     match APP_BASE_URL
```

## QR links in production

QR posters encode `{APP_BASE_URL}/here/{qr_token}`. The redirect logs the scan and 302s
to the storefront. The token is per-placement, so attribution is baked into the URL — no
cookies, no integration. Regenerate posters after `APP_BASE_URL` is final so codes point
at the live host.

## Cost

- Path A: $0.
- Path B: Fly.io free allowance covers one small always-on machine + 1GB volume for a
  hackathon. If it graduates and needs scale, swap SQLite → Postgres (a `DATABASE_URL`
  change in SQLModel) and add Redis for cross-instance SSE.

## Pre-demo checklist

- [ ] `APP_BASE_URL` set to the public URL (tunnel or Fly) and posters regenerated
- [ ] Seed loaded so the dashboard opens populated
- [ ] One physical/on-screen QR ready to scan live
- [ ] Verified: scan → book → dashboard SSE ping with no refresh
- [ ] (Fly) one machine running, `auto_stop_machines = false`
