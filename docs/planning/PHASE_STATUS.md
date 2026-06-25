# Phase Status — current state of the project

> **Purpose:** a single, granular, scannable source of truth for *what is built, what is verified, and
> what is not started*. An agent (or human) picking up this project should read this **first**, then
> [NEXT_PHASE_PLAN.md](NEXT_PHASE_PLAN.md) to choose what to build next.
>
> **Status legend:** ✅ done & verified · 🟡 partial / in progress · ⛔ not started · ⚠️ blocked on an
> external input (credential or decision)
>
> **Last verified:** 2026-06-25 (mocks-first dev mode, 141/141 tests, full E2E — see
> [TESTING.md](../reference/TESTING.md)).
>
> **2026-06-25 update — Phase 4 (Data Ingestion Layer) implemented (fixtures-first).** The ingestion
> spine is complete and credential-free: five knowledge sources → parse (HTML/text) → canonical metadata
> → checksum dedup/versioning → Document Registry (PostgreSQL) → deterministic chunking, with a **hard
> stop before embeddings** (no Qdrant writes — a test asserts the vector store stays empty). Ships
> `app/ingestion/` (sources + offline fixtures, parsers, chunker, metadata extractor, registry
> write-service, orchestrator, scheduler), the `app/worker/runner.py` CLI, an `IngestionRun` bookkeeping
> table (Alembic `0002`, additive/reversible), and an admin-gated ingestion API. Live crawl/NSE/BSE/Drive
> adapters are gated behind `BA_INGEST_LIVE` (default off). The Market Data Provider interface (Source
> 2A) was completed (`get_market_depth` / `get_option_chain` / `subscribe_ticks`). **+31 tests (141
> total), all mocks-first.**
>
> **2026-06-25 update — Phase 6 (RAG System) implemented.** The canonical RAG pipeline is complete:
> real, credential-gated adapters now sit behind every seam — Qdrant hybrid read (dense+sparse →
> server-side RRF, metadata filters at retrieval), hosted cross-encoder reranker (with RRF fallback),
> Ollama Cloud Gemma generation, and the real Sarvam detect/translate adapter (pulled forward from
> Phase 7). Pipeline hardening added: deterministic query expansion, roadmap intent taxonomy with
> company-filter derivation, mock↔Qdrant filter parity, and PostgreSQL text hydration so the citation
> invariant holds on the real read path. **Mocks-first stays the default; 109/109 tests run
> credential-free.** Authoritative phase numbering unchanged: **Phase 4 = Data Ingestion · Phase 5 =
> Embedding · Phase 6 = RAG · Phase 7 = Multilingual.**

---

## Snapshot

| | |
|---|---|
| **Where the code is** | `deliverables/phase_2/brokerassist/` (FastAPI backend + Next.js frontend monorepo) |
| **Run mode today** | `BA_USE_MOCKS=true` — SQLite + in-memory Redis + deterministic mock AI, **zero credentials** |
| **What works end-to-end** | Widget → session → security gate → intent router → market/RAG branch → cited answer, in EN/HI/TA; plus offline ingestion (sources → registry → chunks) feeding the RAG corpus |
| **Test status** | Backend 141/141 pytest · frontend builds all 8 pages · live E2E verified |
| **What's NOT live** | Real AI vendors, real market data, live source crawls (NSE/BSE/Drive), production launch |
| **Next buildable thing (no creds)** | Finish **Phase 7 — Multilingual Layer** (transliteration / STT / TTS / multilingual UI) — mostly mocks-first; or build the standalone widget package |
| **Next thing needing creds** | Live ingestion (`BA_INGEST_LIVE` + source endpoints) and real adapters (Sarvam → Ollama → reranker → Qdrant → TrueData), one at a time |

---

## Phase ledger

| Phase (roadmap) | Scope | Status | Evidence |
|---|---|---|---|
| **0 — Research** | Competitive gap analysis (10 competitors), feature matrix, gap report | ✅ | `deliverables/phase_0/` |
| **1 — UX Design** | IA, personas, 7 journeys, wireframes, content, CTAs, a11y, prototype | ✅ | `deliverables/phase_1/` |
| **2 — System Architecture (+ thin slice)** | Mocks-first NALCO knowledge-RAG thin-slice + widget security | ✅ | `deliverables/phase_2/brokerassist/` |
| **3 — Backend Foundation** | Auth/access control, persistence, abuse control, module APIs, Document Registry, real-infra wiring | ✅ | code + 20 tests |
| **4 — Data Ingestion Layer** | 6 sources → crawl/parse → metadata → dedup → registry → chunk (stops before embeddings) | ✅ (fixtures-first) / ⚠️ live | **Implemented** — `app/ingestion/` (sources + offline fixtures, `parsers.py`, `chunker.py`, `metadata.py`, `registry_service.py`, `orchestrator.py` w/ no-vector guard, `scheduler.py`), `app/worker/runner.py`, `IngestionRun` table + Alembic `0002`, admin ingestion API; 31 Phase-4 tests (141 total). Live crawl/NSE/BSE/NALCO-IR/Drive adapters gated on `BA_INGEST_LIVE` (+ endpoints/creds). Stops before embeddings (Phase 5). → [PHASE_4_PLAN.md](PHASE_4_PLAN.md) |
| **5 — Embedding Pipeline** | chunks → embeddinggemma dense + native sparse → Qdrant `brokerage_kb` (dual-vector, FK-only payload) | ✅ (mocks-first) / ⚠️ live | **Implemented mocks-first** — `services/embedding_pipeline.py`, `adapters/ollama_cloud.py`, `adapters/qdrant_real.py` (dual-vector + dynamic dim), `worker/embed_runner.py`; 31 Phase-5 tests green (51 total). Live path gated on rotated Ollama/Qdrant creds (+ Phase-4 corpus) |
| **6 — RAG System** | hybrid retrieval (dense+sparse) → RRF → rerank → generate → cite | ✅ (mocks-first) / ⚠️ live | **Implemented** — `rag_pipeline.py` (expansion + PG hydration), `services/query_expansion.py`, `services/intent_router.py` (taxonomy + filters), real adapters `adapters/qdrant_real.QdrantReadStore`, `adapters/reranker_cloud.py`, `adapters/ollama_cloud.OllamaCloudLLM`; 58 Phase-6 tests (109 total). Live path gated on Qdrant/reranker/Ollama creds (+ embedded corpus) |
| **7 — Multilingual Layer** | real Sarvam EN/HI/TA detect/translate | 🟡 | **Sarvam detect/translate adapter built early in Phase 6** (`adapters/sarvam_cloud.py`, credential-gated); transliteration / STT / TTS / multilingual UI still to do |
| **8+ — NALCO pilot / nav agent / frontend / launch** | per roadmap | ⛔ ⚠️ | gated on discovery TBDs |
| **(cross-cutting) Real vendor adapters** | Swap mocks for Sarvam / Ollama / reranker / Qdrant / TrueData | ⛔ ⚠️ | **wiring workstream, not a phase** → [NEXT_PHASE_PLAN.md](NEXT_PHASE_PLAN.md) §C; interfaces ready in `adapters/base.py` |

---

## Phase 2/3 — capability-level status (what's actually in the code)

| Capability | Status | Where | Notes |
|---|---|---|---|
| Intent router (market/knowledge fork) | ✅ | `services/intent_router.py` | keyword + known-symbol heuristic |
| Market branch (cached, never Qdrant) | ✅ (mock) | `services/market_service.py` | ⚠️ real = TrueData adapter |
| RAG: translate→expand→embed→hybrid→RRF→rerank→gen→cite | ✅ (mock+real seam) | `services/rag_pipeline.py`, `services/query_expansion.py` | genuine RRF + relevance gate; real Qdrant read = `adapters/qdrant_real.QdrantReadStore` |
| Citations from PostgreSQL (FK-only Qdrant) | ✅ | `rag_pipeline.py` (`_hydrate_text`), `db/models.py` | ADR-002 invariant; real read returns FKs → text/citations from PG |
| Query expansion (recall) | ✅ | `services/query_expansion.py` | deterministic acronym/synonym expansion; `BA_QUERY_EXPANSION_ENABLED` |
| Intent taxonomy + filter derivation | ✅ | `services/intent_router.py` | market/disclosure/navigation/faq/algo; derives company filter |
| Query/response translation EN/HI/TA | ✅ (mock+real) | `adapters/mocks.py`, `adapters/sarvam_cloud.py` | real Sarvam gated on `BA_SARVAM_API_KEY` |
| LLM generation (grounded) | ✅ (mock+real) | `adapters/mocks.py`, `adapters/ollama_cloud.OllamaCloudLLM` | real Gemma gated on Ollama Cloud creds |
| Cross-encoder rerank (+ fallback) | ✅ (mock+real) | `adapters/reranker_cloud.py` | hosted endpoint; degrades to RRF order on outage |
| Widget auth (key hash + Origin allowlist) | ✅ | `core/security.py` | |
| Signed session JWT (30-min) | ✅ | `core/security.py` | |
| Rate limits + per-tenant daily quota | ✅ | `core/ratelimit.py` | Redis hot counter + PG backstop |
| Admin plane (bcrypt, lockout, roles, audit) | ✅ | `core/admin_security.py`, `api/routes_admin.py` | |
| Module APIs (/search /filings /stock) | ✅ | `api/routes_modules.py` | reuse Phase 2 services |
| Normalized schema + Alembic migration | ✅ | `db/models.py`, `alembic/` | 16 tables, `0001_initial` |
| Real Postgres/Redis/Qdrant wiring | ✅ | `docker-compose.yml`, `core/redis.py`, `adapters/qdrant_real.py` | Qdrant = validate-only, no ingestion |
| Observability (JSON logs + correlation id) | ✅ | `core/observability.py` | `/health` `/ready` `/live` |
| Frontend (Next.js, widget, i18n) | ✅ | `apps/frontend/` | 5 pages + assistant widget |
| Market Data Provider interface (Source 2A) | ✅ (mock) | `adapters/base.py`, `adapters/mocks.py` | full interface: LTP/OHLC/depth/option-chain/ticks; real = TrueData adapter |
| **Real vendor adapters** | ✅ built / ⚠️ live-gated | `adapters/__init__.py` | Sarvam / Ollama embed+gen / hosted reranker / Qdrant read+write all wired behind credential gates; default = mocks. Remaining: real market-data (TrueData) |
| **Ingestion → chunk worker (Phase 4)** | ✅ (mocks-first) / ⚠️ live | `app/ingestion/`, `app/worker/runner.py` | discover→parse→metadata→dedup→register→chunk; no vectors (Phase 5 embeds the chunks) |
| **Embedding → Qdrant worker (Phase 5)** | ✅ (mocks-first) / ⚠️ live | `services/embedding_pipeline.py`, `app/worker/embed_runner.py` | chunks → dense+sparse → dual-vector upsert |
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
pytest -q                                   # expect: 141 passed
python -m app.worker.runner --all --once    # Phase 4 ingestion (offline fixtures → registry → chunks)
uvicorn app.main:app --port 8200 &          # then hit /ready, /docs
```
Full quick-start: [SETUP_AND_RUN.md](../reference/SETUP_AND_RUN.md). Detailed plan for what to build
next: [NEXT_PHASE_PLAN.md](NEXT_PHASE_PLAN.md).
