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

Start here: [`backend/MASTER_PLAN.md`](backend/MASTER_PLAN.md) → [`backend/LOCAL_DEV.md`](backend/LOCAL_DEV.md).
