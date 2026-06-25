# Phase Status — current state of the project

> **Purpose:** a single, granular, scannable source of truth for *what is built, what is verified, and
> what is not started*. An agent (or human) picking up this project should read this **first**, then
> [NEXT_PHASE_PLAN.md](NEXT_PHASE_PLAN.md) to choose what to build next.
>
> **Status legend:** ✅ done & verified · 🟡 partial / in progress · ⛔ not started · ⚠️ blocked on an
> external input (credential or decision)
>
> **Last verified:** 2026-06-25 (mocks-first dev mode, 51/51 tests, full E2E — see
> [TESTING.md](../reference/TESTING.md)).
>
> **2026-06-25 update — Phase 5 implemented mocks-first.** The Embedding Pipeline (Phase 5) is now implemented in mocks-first mode with a full suite of unit tests passing. The authoritative phase numbering remains: **Phase 4 = Data Ingestion Layer · Phase 5 = Embedding Pipeline · Phase 6 = RAG · Phase 7 = Multilingual.** Next up: structure Phase 6 — [PHASE_6_KICKOFF.md](PHASE_6_KICKOFF.md) (start from [HANDOFF_TO_PHASE_6.md](HANDOFF_TO_PHASE_6.md)).

---

## Snapshot

| | |
|---|---|
| **Where the code is** | `deliverables/phase_2/brokerassist/` (FastAPI backend + Next.js frontend monorepo) |
| **Run mode today** | `BA_USE_MOCKS=true` — SQLite + in-memory Redis + deterministic mock AI, **zero credentials** |
| **What works end-to-end** | Widget → session → security gate → intent router → market/RAG branch → cited answer, in EN/HI/TA |
| **Test status** | Backend 51/51 pytest · frontend builds all 8 pages · live E2E verified |
| **What's NOT live** | Real AI vendors, real market data, the ingestion/embedding worker, production launch |
| **Next buildable thing (no creds)** | **Phase 4 — Data Ingestion Layer** (design-approved, ready to implement) — see [PHASE_4_PLAN.md](PHASE_4_PLAN.md). Then structure/implement **Phase 6 — RAG System** — see [PHASE_6_KICKOFF.md](PHASE_6_KICKOFF.md). |
| **Next thing needing creds** | Real adapters (Sarvam → Ollama → reranker → Qdrant → TrueData), one at a time |

---

## Phase ledger

| Phase (roadmap) | Scope | Status | Evidence |
|---|---|---|---|
| **0 — Research** | Competitive gap analysis (10 competitors), feature matrix, gap report | ✅ | `deliverables/phase_0/` |
| **1 — UX Design** | IA, personas, 7 journeys, wireframes, content, CTAs, a11y, prototype | ✅ | `deliverables/phase_1/` |
| **2 — System Architecture (+ thin slice)** | Mocks-first NALCO knowledge-RAG thin-slice + widget security | ✅ | `deliverables/phase_2/brokerassist/` |
| **3 — Backend Foundation** | Auth/access control, persistence, abuse control, module APIs, Document Registry, real-infra wiring | ✅ | code + 20 tests |
| **4 — Data Ingestion Layer** | 6 sources → crawl/parse → metadata → dedup → registry → chunk (stops before embeddings) | 🟡 ⛔ | **planned & design-approved, not implemented** → [PHASE_4_PLAN.md](PHASE_4_PLAN.md) |
| **5 — Embedding Pipeline** | chunks → embeddinggemma dense + native sparse → Qdrant `brokerage_kb` (dual-vector, FK-only payload) | ✅ (mocks-first) / ⚠️ live | **Implemented mocks-first** — `services/embedding_pipeline.py`, `adapters/ollama_cloud.py`, `adapters/qdrant_real.py` (dual-vector + dynamic dim), `worker/embed_runner.py`; 31 Phase-5 tests green (51 total). Live path gated on rotated Ollama/Qdrant creds (+ Phase-4 corpus) |
| **6 — RAG System** | hybrid retrieval (dense+sparse) → RRF → rerank → generate → cite | 🟡 | mock pipeline exists (`rag_pipeline.py`); real path later |
| **7 — Multilingual Layer** | real Sarvam EN/HI/TA detect/translate | 🟡 | mock exists; real = Sarvam adapter |
| **8+ — NALCO pilot / nav agent / frontend / launch** | per roadmap | ⛔ ⚠️ | gated on discovery TBDs |
| **(cross-cutting) Real vendor adapters** | Swap mocks for Sarvam / Ollama / reranker / Qdrant / TrueData | ⛔ ⚠️ | **wiring workstream, not a phase** → [NEXT_PHASE_PLAN.md](NEXT_PHASE_PLAN.md) §C; interfaces ready in `adapters/base.py` |

---

## Phase 2/3 — capability-level status (what's actually in the code)

| Capability | Status | Where | Notes |
|---|---|---|---|
| Intent router (market/knowledge fork) | ✅ | `services/intent_router.py` | keyword + known-symbol heuristic |
| Market branch (cached, never Qdrant) | ✅ (mock) | `services/market_service.py` | ⚠️ real = TrueData adapter |
| RAG: translate→embed→hybrid→RRF→rerank→gen→cite | ✅ (mock) | `services/rag_pipeline.py` | genuine RRF + relevance gate |
| Citations from PostgreSQL (FK-only Qdrant) | ✅ | `rag_pipeline.py`, `db/models.py` | ADR-002 invariant |
| Query/response translation EN/HI/TA | ✅ (mock) | `adapters/mocks.py` | ⚠️ real = Sarvam |
| LLM generation (grounded) | ✅ (mock) | `adapters/mocks.py` | ⚠️ real = Gemma (Ollama Cloud) |
| Widget auth (key hash + Origin allowlist) | ✅ | `core/security.py` | |
| Signed session JWT (30-min) | ✅ | `core/security.py` | |
| Rate limits + per-tenant daily quota | ✅ | `core/ratelimit.py` | Redis hot counter + PG backstop |
| Admin plane (bcrypt, lockout, roles, audit) | ✅ | `core/admin_security.py`, `api/routes_admin.py` | |
| Module APIs (/search /filings /stock) | ✅ | `api/routes_modules.py` | reuse Phase 2 services |
| Normalized schema + Alembic migration | ✅ | `db/models.py`, `alembic/` | 16 tables, `0001_initial` |
| Real Postgres/Redis/Qdrant wiring | ✅ | `docker-compose.yml`, `core/redis.py`, `adapters/qdrant_real.py` | Qdrant = validate-only, no ingestion |
| Observability (JSON logs + correlation id) | ✅ | `core/observability.py` | `/health` `/ready` `/live` |
| Frontend (Next.js, widget, i18n) | ✅ | `apps/frontend/` | 5 pages + assistant widget |
| **Real vendor adapters** | ⛔ ⚠️ | `adapters/__init__.py` | each raises `NotImplementedError` |
| **Ingestion/embedding worker** | ⛔ | — | no chunk→embed→upsert pipeline yet |
| **Standalone widget package** | ⛔ | `packages/widget/` | empty placeholder |

---

## External inputs still required (the ⚠️ gate)

From `deliverables/phase_2/discovery/01_information_inventory_filled.md` — **none block the mock pilot;
all block production**:

- **Vendor credentials/approvals:** Ollama Cloud, Sarvam, Qdrant host, re-ranker host, TrueData.
- **Decisions (TBD):** success metrics, launch scope, expected volumes, latency/availability targets,
  RPO/RTO, budget ceiling + cost caps, data retention/deletion, data residency, source-authority
  precedence, operational ownership, compliance/legal sign-off.

Full decision tracking: [DECISIONS_AND_OPEN_ITEMS.md](DECISIONS_AND_OPEN_ITEMS.md).

---

## Load-bearing invariants (do not break when extending)

1. Citations resolve from **PostgreSQL**, never Qdrant (Qdrant payload = FK only). *(ADR-002)*
2. Market data **never** comes from the vector store — separate cached branch. *(ADR-004)*
3. **No model weights run in-process** — every model is a remote call behind an adapter. *(ADR-001)*
4. The **security/abuse gate runs before any paid model call**. *(ADR-005)*
5. **Translate the query to English before retrieval** for multilingual recall.
6. Mocks-first — the full pipeline must keep running with `BA_USE_MOCKS=true` and zero credentials.

---

## How to confirm this status yourself

```bash
cd deliverables/phase_2/brokerassist/apps/backend && source .venv/bin/activate
pytest -q                                   # expect: 20 passed
uvicorn app.main:app --port 8200 &          # then hit /ready, /docs
```
Full quick-start: [SETUP_AND_RUN.md](../reference/SETUP_AND_RUN.md). Detailed plan for what to build
next: [NEXT_PHASE_PLAN.md](NEXT_PHASE_PLAN.md).
