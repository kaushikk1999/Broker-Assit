# BrokerAssist — Phase 2 monorepo (NALCO pilot thin-slice)

Production-shaped, **mocks-first** implementation of the roadmap Phase 2 architecture. One repo,
multiple services; the AI/vendor dependencies are mocked behind clean interfaces so the whole
pipeline runs with zero credentials.

```
brokerassist/
  apps/
    backend/     FastAPI — intent router, market branch, RAG branch, widget security, registry
    frontend/    Next.js — port of the Phase 1 site + embeddable assistant widget
  packages/
    widget/      (placeholder) standalone embeddable widget build target
  infra/         Railway topology notes
  docker-compose.yml   local Postgres + Redis + Qdrant + backend
```

## What it implements (roadmap-aligned)
- **Intent router fork:** market-data intents → Market Service (Redis-cached, never Qdrant);
  knowledge intents → RAG.
- **Canonical RAG pipeline:** Sarvam(detect) → translate query→EN → embeddinggemma → Qdrant
  hybrid (dense+sparse, filters@retrieval) → RRF → Top-20 → cross-encoder rerank → Top-5 →
  Gemma → translate→user-lang → **citations resolved from PostgreSQL** (never from the vector store).
- **Widget security:** per-brokerage public key + Origin domain allowlist + signed session JWT +
  per-session rate limit + per-tenant daily quota (enforced before any LLM/translation call).
- **Multilingual:** EN / HI / TA, query-side translation before retrieval.
- **No model weights in-process:** every model call sits behind an adapter interface.

## Run the backend (no credentials needed for dev)
```bash
cd apps/backend
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8200            # http://localhost:8200/docs
pytest -q                                    # 20 passing tests
```
Dev uses SQLite + in-memory Redis fallback + mock AI. Seed creates a demo tenant
(widget key `demo-public-key`, allowlist `localhost*`) and a superadmin
(`admin@brokerassist.local` / `admin12345`, override via `BA_ADMIN_SEED_PASSWORD`).

Try it:
```bash
# widget (anonymous) session + chat
TOKEN=$(curl -s -X POST localhost:8200/api/v1/session -H "Origin: http://localhost" \
  -H "Content-Type: application/json" -d '{"widget_key":"demo-public-key"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['session_token'])")
curl -s -X POST localhost:8200/api/v1/chat -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"message":"Explain NALCO latest quarterly result"}'
# discrete modules: /search /filings /stock   (same Bearer session token)
# admin plane
ATOK=$(curl -s -X POST localhost:8200/api/v1/admin/login -H "Content-Type: application/json" \
  -d '{"email":"admin@brokerassist.local","password":"admin12345"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['admin_token'])")
curl -s localhost:8200/api/v1/admin/tenants -H "Authorization: Bearer $ATOK"
```

## Phase 3 — production infra (PostgreSQL / Redis / Qdrant)
```bash
docker compose up -d postgres redis qdrant     # from brokerassist/
cd apps/backend && cp .env.example .env        # fill BA_DATABASE_URL, BA_REDIS_URL, BA_QDRANT_URL, BA_QDRANT_API_KEY
alembic upgrade head                           # apply migrations (instead of dev create_all)
uvicorn app.main:app --port 8200               # startup validates the Qdrant collection
```
`/ready` reports postgres/redis/qdrant status. **Secrets:** never commit a filled `.env`; rotate any
key shared in plaintext (Qdrant/Ollama). Ollama key is stored but unused until Phase 5 (embeddings).

## Run the frontend
```bash
cd apps/frontend
npm install
NEXT_PUBLIC_API_BASE=http://localhost:8200 npm run dev   # http://localhost:3000
```

## Promote to real services
Swap SQLite→PostgreSQL and add Redis/Qdrant via `docker-compose up` (mirrors Railway). Flip
`BA_USE_MOCKS=false` and provide `BA_OLLAMA_*`, `BA_SARVAM_API_KEY`, `BA_RERANKER_URL`,
`BA_QDRANT_URL`, market-data creds — implementing the real adapters behind `app/adapters/base.py`.

## Scope / status
Pilot thin-slice: knowledge RAG + market branch + widget security, all mock-backed. Background
worker (ingestion/embedding) and real vendor adapters are deferred (next workstreams).
