# HERE by Headout — Architecture

Diagrams for the partner-flow demo backend (FastAPI + SQLite + SSE). All diagrams are
Mermaid and render inline on GitHub. See `MASTER_PLAN.md` for the written plan and
`TESTING.md` for the contract these diagrams implement.

## 1. System context

Who uses it and what it talks to. One process, one file — no external services.

```mermaid
flowchart LR
    partner([Partner<br/>hotel, cafe, host]):::actor
    guest([Guest<br/>scans a QR]):::actor

    subgraph sys[HERE by Headout - demo]
      app[FastAPI app<br/>API + QR + tracking + analytics + SSE]:::svc
      db[(SQLite file<br/>here.db)]:::store
      fe[Static frontend<br/>demo/frontend]:::web
    end

    partner -->|set up place, view dashboard| fe
    guest -->|scan QR poster| app
    fe <-->|JSON + SSE| app
    app --> db

    classDef actor fill:#ede9fe,stroke:#7c3aed,color:#3b0764;
    classDef svc fill:#faf5ff,stroke:#a855f7,color:#3b0764;
    classDef store fill:#ecfeff,stroke:#06b6d4,color:#083344;
    classDef web fill:#f0fdf4,stroke:#22c55e,color:#052e16;
```

## 2. Components

Inside the FastAPI process. The SSE bus is a plain in-process asyncio fan-out (single
worker), so "live" needs no Redis and no replication.

```mermaid
flowchart TB
    subgraph fe[Frontend - demo/frontend, served by StaticFiles]
      s01[01 place setup]
      s02[02 QR kit]
      store[guest storefront]
      s03[03 dashboard]
    end

    subgraph api[FastAPI - demo/backend/app]
      direction TB
      r_places[routers/places]
      r_track[routers/tracking<br/>/here, /events]
      r_book[routers/bookings]
      r_stream[routers/stream<br/>SSE]
      r_an[routers/analytics]
      svc_qr[services/qr - segno]
      svc_pos[services/posters - Pillow]
      util[utils<br/>slugify, commission]
      bus[[events_bus<br/>in-process fan-out]]
      dbdep[db.get_session]
    end

    db[(SQLite here.db)]

    s01 --> r_places
    s02 --> r_places
    s02 --> svc_pos
    store --> r_track
    store --> r_book
    s03 --> r_an
    s03 -. EventSource .-> r_stream

    r_places --> util
    svc_pos --> svc_qr
    r_book --> util
    r_book --> bus
    bus --> r_stream
    r_places --> dbdep
    r_track --> dbdep
    r_book --> dbdep
    r_an --> dbdep
    dbdep --> db
```

## 3. Data model

```mermaid
erDiagram
    PARTNER ||--o{ PLACE : owns
    PLACE   ||--o{ PLACEMENT : has
    PLACEMENT ||--o{ EVENT : logs
    PLACEMENT ||--o{ BOOKING : earns

    PARTNER {
        uuid id PK
        string email
        datetime created_at
    }
    PLACE {
        uuid id PK
        uuid partner_id FK
        string name
        string type
        string location
        string slug "unique"
        datetime created_at
    }
    PLACEMENT {
        uuid id PK
        uuid place_id FK
        string label
        string surface_slug
        string qr_token "unique"
        datetime created_at
    }
    EVENT {
        uuid id PK
        uuid placement_id FK
        string kind "impression|scan|chat|rec"
        datetime created_at
    }
    BOOKING {
        uuid id PK
        uuid placement_id FK
        string experience
        float gmv
        float commission "gmv * 0.08"
        datetime created_at
    }
```

The dashboard funnel is `GROUP BY placement_id` over `EVENT` + `BOOKING` — the hardcoded
`surfaceData` object in the prototype collapses into one query.

## 4. Key flows

### 4a. Partner setup → QR kit (screens 01 → 02)

```mermaid
sequenceDiagram
    actor P as Partner
    participant FE as Frontend
    participant API as FastAPI
    participant DB as SQLite

    P->>FE: name place, pick type, choose QR spots
    FE->>API: POST /places {placeName, placements[]}
    API->>API: slugify(name), make unique qr_token per spot
    API->>DB: INSERT place + placements
    API-->>FE: {slug, placements:[{surfaceSlug, qrToken, url}]}
    P->>FE: open QR kit
    FE->>API: GET /places/{slug}/posters
    loop per placement
        API->>API: segno QR for /here/{qr_token}
        API->>API: Pillow composite onto poster artwork
    end
    API-->>FE: poster list + PNG urls
```

### 4b. The money loop: scan → book → live dashboard

This is the demo. A scan is attributed by `qr_token`; a booking publishes to the SSE bus
and lands on the dashboard with no refresh.

```mermaid
sequenceDiagram
    actor G as Guest
    participant SF as Storefront
    participant API as FastAPI
    participant DB as SQLite
    participant BUS as Event Bus
    participant DASH as Dashboard

    DASH->>API: GET /stream (SSE, held open)
    API->>BUS: subscribe

    G->>API: GET /here/{qr_token}
    API->>DB: INSERT event(kind=scan)
    API-->>G: 302 -> storefront?place=&surface=
    G->>SF: lands on co-branded storefront
    SF->>API: POST /events (impression|chat|rec)
    G->>SF: tap "Book"
    SF->>API: POST /bookings {qr_token, experience, gmv}
    API->>API: commission = round(gmv * 0.08, 2)
    API->>DB: INSERT booking
    API->>BUS: publish(booking)
    BUS-->>API: fan-out to subscribers
    API-->>DASH: data: {experience, commission, surface}
    DASH->>DASH: live ping + tiles increment
```

### 4c. Analytics aggregation (screen 03)

```mermaid
sequenceDiagram
    participant DASH as Dashboard
    participant API as FastAPI
    participant DB as SQLite

    DASH->>API: GET /analytics/{slug}
    API->>DB: SELECT events GROUP BY placement, kind
    API->>DB: SELECT bookings GROUP BY placement
    API->>API: per-surface rows + totals; conversion = bookings/scans
    API-->>DASH: {totals, surfaces[]}
```

## 5. Deployment topology

### 5a. Demo — local + Cloudflare Tunnel ($0, nothing deployed)

```mermaid
flowchart LR
    phone([Guest phone]):::actor
    judge([Judge browser]):::actor
    cf{{Cloudflare Tunnel<br/>*.trycloudflare.com}}:::edge
    subgraph laptop[Your laptop]
      uap[uvicorn app.main:app]:::svc
      db[(here.db file)]:::store
    end
    phone -->|scan QR| cf
    judge -->|open dashboard| cf
    cf --> uap
    uap --> db

    classDef actor fill:#ede9fe,stroke:#7c3aed,color:#3b0764;
    classDef edge fill:#fff7ed,stroke:#f97316,color:#7c2d12;
    classDef svc fill:#faf5ff,stroke:#a855f7,color:#3b0764;
    classDef store fill:#ecfeff,stroke:#06b6d4,color:#083344;
```

### 5b. Durable — Fly.io + volume

```mermaid
flowchart LR
    users([Partners + Guests]):::actor
    subgraph fly[Fly.io - one machine, single worker]
      proc[uvicorn :8080<br/>auto_stop = false to hold SSE]:::svc
      vol[(volume /data/here.db)]:::store
      fr[/frontend - StaticFiles/]:::web
    end
    users -->|https| proc
    proc --> vol
    proc --- fr

    classDef actor fill:#ede9fe,stroke:#7c3aed,color:#3b0764;
    classDef svc fill:#faf5ff,stroke:#a855f7,color:#3b0764;
    classDef store fill:#ecfeff,stroke:#06b6d4,color:#083344;
    classDef web fill:#f0fdf4,stroke:#22c55e,color:#052e16;
```

> Single worker is deliberate: the SSE fan-out is in-process. Scaling to multiple
> machines/workers would need a shared bus (e.g. Redis pub/sub) — out of scope for the
> hackathon, noted here so the constraint is explicit.

## 6. Build = test milestones

```mermaid
flowchart LR
    m1[1 scaffold<br/>app boots] --> m2[2 places]
    m2 --> m3[3 posters]
    m3 --> m4[4 scan]
    m4 --> m5[5 bookings]
    m5 --> m6[6 SSE + analytics]
    m6 --> m7[7 seed + verify loop]
    m7 --> m8[8 host]
```

Each box has a matching test group in `tests/` (see `TESTING.md`) — build until it's green.
