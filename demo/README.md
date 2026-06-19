# HERE by Headout — Demo Project

The **target demo**: the partner flow backed by a real backend (FastAPI + SQLite + SSE),
with the frontend wired to the API so QR scans, bookings, and the live dashboard are real.

```
demo/
  backend/    FastAPI app + plan docs (MASTER_PLAN.md, LOCAL_DEV.md, HOSTING.md)
  frontend/   copy of the static prototype, wired to the API
```

**Fallback:** the original static prototype is frozen at the repo root in `designs/` and
is never touched by backend work. If this demo breaks, `designs/` still stands alone.

Docs:
- [`backend/MASTER_PLAN.md`](backend/MASTER_PLAN.md) — the plan (stack, data model, API, milestones)
- [`backend/ARCHITECTURE.md`](backend/ARCHITECTURE.md) — diagrams (context, components, ER, flows, deploy)
- [`backend/LOCAL_DEV.md`](backend/LOCAL_DEV.md) — run it locally (no Docker)
- [`backend/TESTING.md`](backend/TESTING.md) — the test-driven contract
- [`backend/HOSTING.md`](backend/HOSTING.md) — tunnel + Fly.io deploy
