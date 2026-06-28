# Phase Status — current state of the project

> **Purpose:** a single, granular, scannable source of truth for *what is built, what is verified, and
> what is not started*. An agent (or human) picking up this project should read this **first**, then
> [NEXT_PHASE_PLAN.md](NEXT_PHASE_PLAN.md) to choose what to build next.
>
> **Status legend:** ✅ done & verified · 🟡 partial / in progress · ⛔ not started · ⚠️ blocked on an
> external input (credential or decision)
>
> **Last verified:** 2026-06-26 (142/142 tests; mocks-first stays credential-free, and a real-vendor
> E2E was run against live data — see the 2026-06-26 updates below and [TESTING.md](../reference/TESTING.md)).
>
> **2026-06-26 update (b) — real dense embeddings wired (Qwen3 via local Ollama sidecar).** The "dense
> embeddings stay mock" caveat is now resolved for local testing. Ollama Cloud's `/api/embed` is 401 for
> every model on this plan (and `qwen3.5`/qwen3 *cloud* generation needs a paid subscription), so dense
> embeddings now run on a **separate local Ollama server** (`qwen3-embedding:0.6b`, **1024-dim**) pointed
> at by the new **`BA_OLLAMA_EMBED_URL`** setting — a remote call behind the adapter, so **no model
> weights run in the FastAPI process (ADR-001 holds)**. Generation stays on **gemma4:31b-cloud** (owner
> choice; qwen3 cloud gen gated behind a subscription). Recreated `brokerage_kb` at dim 1024 and
> re-embedded all 64 docs; verified **real semantic retrieval** (a paraphrased query with no keyword
> overlap — "is the aluminium company offloading bulk refined ore?" — correctly retrieved NALCO's
> calcined-alumina sale notices) and the EN/HI pipeline end-to-end. Call routing confirmed: embeddings →
> `localhost:11434`, generation → `ollama.com`, rerank → Jina, translate → Sarvam. **142 tests still
> green** (tests ignore `.env`). New decision **P5-D4**; prod still needs a hosted Ollama/embedding
> endpoint (open input).
>
> **2026-06-26 update (a) — live knowledge ingestion wired + real-vendor E2E verified.** Three Phase-4 live
> source adapters are now implemented (previously `NotImplementedError` stubs), all gated behind
> `BA_INGEST_LIVE=true`: **NSE** corporate filings via the official JSON API (roadmap "Official APIs
> where available" — no browser needed), **NALCO IR** via server-rendered HTML crawl of
> nalcoindia.com/investor-services (httpx), and **BSE** via a Playwright browser context. BSE is fronted
> by **Akamai Bot Manager**, which blocks datacenter IPs at the edge, so from this environment it returns
> 0 docs *gracefully* (no run failure); the same code works from an allow-listed IP/residential proxy.
> Ran the full real pipeline with `.env` creds (Qdrant + Ollama Cloud `gemma4:31b-cloud` + Sarvam + Jina
> reranker, all live): crawled **25 NSE filings + 30 NALCO IR notices** → embedded → Qdrant
> `brokerage_kb` (64 docs / 66 points) → answered EN + HI chat queries with correct PostgreSQL citations
> (e.g. NALCO "Saksham Niveshak" campaign, calcined-alumina sale tenders, JINDALSAW credit rating).
> **Caveats:** at the time of this run dense embeddings were still the deterministic **mock** (since
> superseded — see update (b) above, which wired real Qwen3 dense embeddings); **market data stays mock**
> — quotes come from an API key, never crawling (ADR-004). Mocks-first remains the default (tests run
> with `BA_DISABLE_DOTENV=1`). **+1 test (142 total).** New decisions: **P4-D8…P4-D10** in
> [DECISIONS_AND_OPEN_ITEMS.md](DECISIONS_AND_OPEN_ITEMS.md).
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
| **What works end-to-end** | Widget → session → security gate → intent router → market/RAG branch → cited answer, in EN/HI/TA; plus offline ingestion (sources → registry → chunks) feeding the RAG corpus. **Also verified against live data (2026-06-26):** real NSE + NALCO IR crawl → embed → Qdrant → Jina rerank → Gemma 4 generation → Sarvam translate → PG citations |
| **Test status** | Backend 142/142 pytest · frontend builds all 8 pages · live E2E verified (mock + real-vendor) |
| **What's NOT live** | Real market data, **BSE crawl (Akamai-blocked from datacenter IPs)**, Google Drive + broker-site crawls, production launch. Dense embeddings now real via a **local** Ollama sidecar (Qwen3) — prod still needs a hosted Ollama/embedding endpoint |
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
| **4 — Data Ingestion Layer** | 6 sources → crawl/parse → metadata → dedup → registry → chunk (stops before embeddings) | ✅ (fixtures-first) / ⚠️ live | **Implemented** — `app/ingestion/` (sources + offline fixtures, `parsers.py`, `chunker.py`, `metadata.py`, `registry_service.py`, `orchestrator.py` w/ no-vector guard, `scheduler.py`), `app/worker/runner.py`, `IngestionRun` table + Alembic `0002`, admin ingestion API; 32 Phase-4 tests (142 total). **Live adapters wired (2026-06-26):** NSE (official JSON API) + NALCO IR (HTML crawl) ✅ verified E2E; BSE (Playwright) ⚠️ Akamai-blocked from datacenter IPs → graceful 0 docs; broker-site + Google Drive still stubs. All gated on `BA_INGEST_LIVE` (default off). Stops before embeddings (Phase 5). → [PHASE_4_PLAN.md](PHASE_4_PLAN.md) |
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
| **Ingestion → chunk worker (Phase 4)** | ✅ (mocks-first) / 🟡 live | `app/ingestion/`, `app/worker/runner.py`, `app/ingestion/sources/live_sources.py` | discover→parse→metadata→dedup→register→chunk; no vectors (Phase 5 embeds the chunks). Live: NSE + NALCO IR wired & verified; BSE wired but Akamai-blocked here; broker-site + Drive stubs |
| **Embedding → Qdrant worker (Phase 5)** | ✅ (mocks-first) / ✅ live (local) | `services/embedding_pipeline.py`, `app/worker/embed_runner.py`, `adapters/ollama_cloud.py` | chunks → dense+sparse → dual-vector upsert. **Real dense now wired:** `qwen3-embedding:0.6b` (1024-dim) via `BA_OLLAMA_EMBED_URL` (local Ollama sidecar); `brokerage_kb` recreated at dim 1024, 64 docs re-embedded |
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
pytest -q                                   # expect: 142 passed
python -m app.worker.runner --all --seed --once  # Phase 4 ingestion (--seed bootstraps schema on a fresh DB; offline fixtures → registry → chunks)
uvicorn app.main:app --port 8200 &          # then hit /ready, /docs

# Optional — live knowledge ingestion (needs .env creds + BA_INGEST_LIVE=true; live deps in requirements-ingest.txt):
python -m app.worker.runner --source nse --once       # real NSE corporate filings (official JSON API)
python -m app.worker.runner --source nalco_ir --once  # real NALCO IR notices (HTML crawl)
python -m app.worker.embed_runner --once              # embed the new chunks → Qdrant
```
Full quick-start: [SETUP_AND_RUN.md](../reference/SETUP_AND_RUN.md). Detailed plan for what to build
next: [NEXT_PHASE_PLAN.md](NEXT_PHASE_PLAN.md).
