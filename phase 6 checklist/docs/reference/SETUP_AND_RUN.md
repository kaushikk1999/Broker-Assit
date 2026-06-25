# Setup & Run Guide

Everything needed to run BrokerAssist locally, from a clean machine to a working widget — plus how to
move from mocks to real infrastructure and vendors.

> The application lives in [`deliverables/phase_2/brokerassist/`](../../deliverables/phase_2/brokerassist/).
> All paths below are relative to that directory unless noted.

---

## 1. Prerequisites

| Tool | Version | Used for |
|---|---|---|
| Python | **3.11** | Backend (FastAPI) |
| Node.js | **18+** (tested on 22) | Frontend (Next.js 14) |
| Docker + Docker Compose | latest | Optional — real Postgres/Redis/Qdrant |

Dev mode needs **none** of Postgres/Redis/Qdrant/AI credentials — it uses SQLite + an in-memory Redis
fallback + deterministic mock AI.

---

## 2. Run the backend (zero credentials)

```bash
cd deliverables/phase_2/brokerassist/apps/backend
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8200
```

- API root: <http://localhost:8200/>
- **Interactive API docs (Swagger):** <http://localhost:8200/docs>
- Health: <http://localhost:8200/health> · Readiness: <http://localhost:8200/ready>

On startup the app **seeds itself idempotently** (`db/seed.py`): creates tables, a demo tenant, a
widget key, a domain allowlist, a superadmin, and the NALCO knowledge base.

### Seeded dev credentials

| Thing | Value |
|---|---|
| Demo widget key | `demo-public-key` |
| Allowed Origins | `localhost`, `127.0.0.1`, `localhost:3000`, `localhost:8123` |
| Superadmin email | `admin@brokerassist.local` |
| Superadmin password | `admin12345` (override with `BA_ADMIN_SEED_PASSWORD`) |
| Knowledge base | 4 NALCO/algo documents (results, board outcome, dividend history, algo FAQ) |

### Smoke-test it from the shell

```bash
# 1) open a widget session (Origin must be allowlisted)
TOKEN=$(curl -s -X POST localhost:8200/api/v1/session \
  -H "Origin: http://localhost:3000" -H "Content-Type: application/json" \
  -d '{"widget_key":"demo-public-key"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['session_token'])")

# 2) ask a knowledge question (cited answer)
curl -s -X POST localhost:8200/api/v1/chat -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"message":"Explain NALCO latest quarterly result"}'

# 3) ask a market question (cached quote)
curl -s -X POST localhost:8200/api/v1/chat -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"message":"What is the LTP of NALCO?"}'
```

Full endpoint catalogue: [API_REFERENCE.md](API_REFERENCE.md).

---

## 3. Run the frontend

```bash
cd deliverables/phase_2/brokerassist/apps/frontend
npm install
NEXT_PUBLIC_API_BASE=http://localhost:8200 npm run dev      # http://localhost:3000
```

The client defaults to `http://localhost:8200` and widget key `demo-public-key` even with no env vars,
so it works against the backend above out of the box. Open <http://localhost:3000>, click **"Try the
assistant"**, and the widget will create a session and stream a cited answer from the backend.

Production build (also the strongest correctness check — type-checks + static-generates all pages):

```bash
npm run build && npm start
```

---

## 4. Configuration reference

Backend settings live in `apps/backend/app/config.py`, all read from environment variables with the
**`BA_`** prefix (a `.env` file is supported). The most important:

| Variable | Default | Meaning |
|---|---|---|
| `BA_USE_MOCKS` | `true` | Master switch — mock AI vs real vendors |
| `BA_DATABASE_URL` | `sqlite:///./brokerassist.db` | SQLite (dev) or `postgresql://…` (prod) |
| `BA_REDIS_URL` | _(empty)_ | Real Redis when set; in-memory fallback otherwise |
| `BA_SESSION_JWT_SECRET` | `dev-only-change-me` | **Change in production** |
| `BA_ADMIN_JWT_SECRET` | `dev-only-change-me-admin` | **Change in production** |
| `BA_SESSION_TTL_SECONDS` | `1800` | Widget session lifetime |
| `BA_RATE_LIMIT_PER_SESSION_PER_MIN` | `20` | Per-session rate limit |
| `BA_RATE_LIMIT_PER_IP_PER_MIN` | `40` | Per-IP rate limit |
| `BA_TENANT_DAILY_QUOTA` | `5000` | Default per-tenant daily cap |
| `BA_RETRIEVE_TOP_K` / `BA_RERANK_TOP_K` | `20` / `5` | RAG retrieval / rerank sizes |
| `BA_SUPPORTED_LANGUAGES` | `en,hi,ta` | Supported languages |
| `BA_QDRANT_URL` / `BA_QDRANT_API_KEY` | _(empty)_ | Qdrant connection (Phase 3 validates only) |
| `BA_QDRANT_COLLECTION` | `brokerassist_knowledge` | Collection name |
| `BA_QDRANT_VALIDATE_ON_STARTUP` | `true` | Validate collection contract at boot |
| `BA_OLLAMA_API_KEY` / `BA_SARVAM_API_KEY` / `BA_RERANKER_URL` | _(empty)_ | Real vendor creds (unused while mocked) |

Frontend env (`apps/frontend/.env.local`, see `.env.local.example`):

| Variable | Default | Meaning |
|---|---|---|
| `NEXT_PUBLIC_API_BASE` | `http://localhost:8200` | Backend base URL |
| `NEXT_PUBLIC_WIDGET_KEY` | `demo-public-key` | Tenant widget key |

> **Secrets:** never commit a filled `.env`. Rotate any key ever shared in plaintext. The root
> `.gitignore` already excludes `.env` (but keeps `*.example`).

---

## 5. Run with real infrastructure (Postgres + Redis + Qdrant)

Still mocks-first for AI, but exercises the real datastores and migrations:

```bash
cd deliverables/phase_2/brokerassist
docker compose up -d postgres redis qdrant      # brings up the three stores

cd apps/backend
cp .env.example .env                            # fill BA_DATABASE_URL, BA_REDIS_URL, BA_QDRANT_URL, ...
alembic upgrade head                            # apply migrations (instead of dev create_all)
uvicorn app.main:app --port 8200                # startup validates the Qdrant collection contract
```

`/ready` now reports live `postgres` / `redis` / `qdrant` status. The whole stack (including the
backend container) can also be started with `docker compose up`.

---

## 6. Promote to real vendors (next workstream)

1. Set `BA_USE_MOCKS=false`.
2. Provide `BA_OLLAMA_API_KEY` (embeddinggemma + Gemma), `BA_SARVAM_API_KEY` (language),
   `BA_RERANKER_URL` (hosted cross-encoder), `BA_QDRANT_URL` + `BA_QDRANT_API_KEY`, and market-data
   credentials.
3. Implement the real adapters behind the interfaces in `app/adapters/base.py` (the factory in
   `app/adapters/__init__.py` currently raises `NotImplementedError` for each until wired).

Because every model sits behind an adapter, **callers don't change** — only the adapter implementations
do. See the [readiness scorecard](../../deliverables/phase_2/discovery/03_readiness_scorecard.md) for the
exact ⚠️ items each vendor unblocks.

---

## 7. Deployment topology

- **Monorepo, multi-service**, targeting **Railway** (notes in
  `deliverables/phase_2/brokerassist/infra/railway.md`).
- Backend serves on `:8200`; frontend on `:3000`.
- `client_ip()` is proxy-aware (reads `X-Forwarded-For`) for correct rate-limiting behind Railway's
  proxy.

---

## 8. Common issues

| Symptom | Cause / fix |
|---|---|
| `403 Origin '…' not allowlisted` | The request `Origin` isn't in the tenant allowlist — use `http://localhost:3000` in dev, or add the domain via the admin API. |
| `401 Invalid widget key` | Wrong/rotated key — dev key is `demo-public-key`. |
| `401 Session expired` | Session JWT older than 30 min — create a new session. |
| `429 Rate limit / Daily quota` | Hit a per-session/IP limit or the tenant daily quota — expected abuse control. |
| `/ready` shows `redis: memory` | No `BA_REDIS_URL` set — in-memory fallback (fine for dev, not multi-process). |
| Qdrant `skipped` at startup | `BA_QDRANT_URL` not set — expected in mock dev mode. |
