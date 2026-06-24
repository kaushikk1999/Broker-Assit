# Architecture Decision Records (Phase 2 pilot)

## ADR-001 — Mocks-first provider interfaces
**Status:** Accepted. **Context:** No vendor credentials yet; roadmap forbids model weights in-process.
**Decision:** Every external dependency (language, embedding, vector store, re-ranker, LLM,
market-data) sits behind an ABC in `apps/backend/app/adapters/base.py`; a deterministic mock
implements each. A factory (`app/adapters/__init__.py`) returns mock or real by `BA_USE_MOCKS`.
**Consequences:** Full pipeline runs with zero credentials; real vendors drop in without touching
callers. Mock retrieval/answer quality is illustrative, not production-grade.

## ADR-002 — Citations resolved from PostgreSQL, not the vector store
**Status:** Accepted. **Decision:** Qdrant payload carries only `(document_id, chunk_id)`; all
citation fields come from the `documents` registry in PostgreSQL (modeled in `app/db/models.py`).
**Consequences:** Single source of truth for citations; vector store can be re-indexed freely.

## ADR-003 — SQLite for dev, PostgreSQL for prod (same models)
**Status:** Accepted. **Decision:** One SQLAlchemy model layer; `BA_DATABASE_URL` selects the engine.
**Consequences:** Zero-setup local runs; production parity via docker-compose / Railway Postgres.

## ADR-004 — Intent routing fork before retrieval
**Status:** Accepted. **Decision:** `services/intent_router.classify` splits market-data vs knowledge;
market path uses the Market Service + cache and never touches Qdrant.
**Consequences:** Market data stays authoritative/live; RAG cost only paid for knowledge intents.

## ADR-005 — Abuse/cost control before any model call
**Status:** Accepted. **Decision:** `core/ratelimit` enforces per-session rate + per-tenant daily
quota inside `/chat` before language/LLM calls. Redis in prod; in-memory fallback in dev.
**Consequences:** Runaway cost and abuse bounded at the edge of the public widget.

## Open ADRs (to write before production)
ADR-006 Qdrant hosting · ADR-007 Re-ranker provider · ADR-008 Market-data vendor + licensing ·
ADR-009 Source-authority precedence · ADR-010 Secrets management on Railway.
