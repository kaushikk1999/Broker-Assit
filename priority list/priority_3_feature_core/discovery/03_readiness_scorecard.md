# Phase 2 — Readiness Scorecard

| Capability | Pilot (mocks) | Production (real vendors) |
|---|---|---|
| Intent router (market/knowledge fork) | ✅ Done | ✅ reusable |
| Market-data branch (cache, no-Qdrant) | ✅ Done (mock provider) | ⚠️ needs TrueData adapter + creds |
| RAG: hybrid retrieval + RRF + rerank | ✅ Done (mock Qdrant/re-ranker) | ⚠️ needs Qdrant + hosted re-ranker |
| Query/response translation (EN/HI/TA) | ✅ Done (mock Sarvam) | ⚠️ needs Sarvam key |
| LLM generation | ✅ Done (grounded mock) | ⚠️ needs Ollama Cloud (Gemma) |
| Citations from PostgreSQL registry | ✅ Done | ✅ reusable |
| Widget auth (key + Origin allowlist) | ✅ Done | ✅ reusable |
| Signed session tokens | ✅ Done | ✅ reusable |
| Rate limit + per-tenant quota | ✅ Done (in-memory) | ⚠️ swap to Redis |
| PostgreSQL registry/models/migrations | ✅ Done (SQLite dev) | ⚠️ point to Railway Postgres |
| Background worker (ingestion/embedding) | ⛔ Deferred | ⛔ next workstream |
| Frontend (Next.js + widget) | ◐ Port in progress | ⚠️ wire to prod backend |
| Tests | ✅ 8 passing | — |

**Verdict:** the pilot thin-slice is **built and verified end-to-end against mocks**. Production
readiness is gated on vendor accounts/credentials and the ⚠️ discovery inputs — not on more design.
