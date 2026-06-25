# Railway deployment topology (Phase 2)

Monorepo → multiple Railway services (one repo, separate deploys). No model weights run in any
Railway service; LLM/embeddings/rerank/translation are remote calls.

## Services (Railway Pro project)
| Service | Source | Notes |
|---|---|---|
| `frontend` | `apps/frontend` | Next.js. Env: `NEXT_PUBLIC_API_BASE` → backend URL |
| `backend` | `apps/backend` (Dockerfile) | FastAPI. Reads `BA_*` env; start `uvicorn app.main:app` |
| `worker` | `apps/backend` | Background workers (run OFF the web process): Phase 4 ingestion `python -m app.worker.runner --all --once` (sources→registry→chunks) and Phase 5 embedding `python -m app.worker.embed_runner --once` (chunks→Qdrant). Cron cadences (`BA_INGEST_CRON_*`) live here only |
| `postgres` | Railway plugin | `BA_DATABASE_URL` (registry, tenants, quotas, citations) |
| `redis` | Railway plugin | `BA_REDIS_URL` (cache, rate-limit, quotas) |
| `qdrant` | Railway template/service or Qdrant Cloud | `BA_QDRANT_URL` (dense+sparse vectors, FK payload) |

## External (off-Railway) hosted services
Ollama Cloud (Gemma + embeddinggemma) · Sarvam AI · hosted cross-encoder re-ranker · market-data
vendor (TrueData primary). Set `BA_USE_MOCKS=false` and the corresponding `BA_*` keys to switch on.

## Env per service (backend)
`BA_USE_MOCKS`, `BA_DATABASE_URL`, `BA_REDIS_URL`, `BA_QDRANT_URL`, `BA_OLLAMA_*`, `BA_SARVAM_API_KEY`,
`BA_RERANKER_URL`, `BA_MARKETDATA_PROVIDER`, `BA_SESSION_JWT_SECRET`.

## Promotion path
mocks-first (current) → add Postgres/Redis/Qdrant plugins (docker-compose mirrors this locally) →
wire real AI vendors one adapter at a time behind the existing interfaces (`app/adapters/base.py`).
