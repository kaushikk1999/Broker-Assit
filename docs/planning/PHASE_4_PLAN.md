# Phase 4 — Data Ingestion Layer (design-approved plan)

> **Status:** 🟡 **Analyzed & design-approved — NOT yet implemented.** This is the authoritative,
> ready-to-build plan for roadmap **Phase 4**. It supersedes the older "Phase 4 = Real Vendor Adapters"
> label that appears in some project docs (see the [phase-numbering correction](#phase-numbering-correction)).
>
> **Source of truth:** `AI_Brokerage_Assistant_Roadmap_Merged` roadmap, pp. 11–16.
> **Scope discipline:** Phase 4 stops **before** embeddings/Qdrant writes — that tail is **Phase 5**
> (see [PHASE_5_KICKOFF.md](PHASE_5_KICKOFF.md)).

---

## 1. Goal

> *"Build data ingestion before AI."* — roadmap p. 11

Turn the six external knowledge/data sources into **clean, deduplicated, registered, chunked documents
in PostgreSQL**, ready for Phase 5 to embed into Qdrant. Market data is a separate, cached, non-Qdrant
branch.

## 2. Locked design decisions (approved 2026-06-24)

| # | Decision | Choice | Why |
|---|---|---|---|
| **P4-D1** | Pipeline seam vs embeddings | **Stop at chunking.** Phase 4 produces `DocumentChunk` rows; Phase 5 embeds + writes Qdrant. | Honors "no embeddings in Phase 4"; cleanest seam; deterministic (no model calls). |
| **P4-D2** | Live sources this phase | **Fixtures + opt-in live adapters.** Full pipeline runs on deterministic offline fixtures; real crawler/NSE/BSE/Drive adapters are gated behind `BA_INGEST_LIVE` (default `false`) + optional-dependency extras. | Keeps mocks-first/CI credential- and network-free; avoids NSE/BSE anti-bot/ToS coupling. |
| **P4-D3** | Scheduling | **Run-once commands + worker + config cadences.** `python -m app.worker.runner --source <s> --once`; cron wired in the Railway **worker only**, never the web process. | Testable offline now; safe to schedule later; no live fetches in web/CI. |

## 3. The six sources (roadmap pp. 11–16)

| # | Source | Connection | Collect | Refresh | Phase-4 output (stops here) |
|---|---|---|---|---|---|
| 1 | Broker Website | Sitemap + crawl (Crawl4AI/Firecrawl/Playwright) | Home, About, FAQ, Pricing, Products, KYC, Open Account, Algo, Research, Contact | Daily @ 2 AM | cleaned text → registry → chunks |
| 2A | **Market Data Layer** | REST + WebSocket (TrueData primary; Ticker/exchange/future) | LTP, OHLC, Market Depth, Volume, Option Chain | Real-time | **Not registry/chunks** — cached in Redis, served by Market Service. Never crawled, never Qdrant. |
| 2B | NSE Corporate Filings | Official API; fallback structured crawl (Requests/Playwright/BS4) | Quarterly results, announcements, shareholding, board meetings, corporate actions | Hourly | parsed → metadata → registry → chunks |
| 3 | BSE India | Structured crawl (Playwright/BS4) | Results, filings, corporate actions, disclosures | Hourly | parsed → metadata → registry → chunks |
| 4 | NALCO Investor Relations | Website crawl (Crawl4AI/Playwright) | Annual reports, presentations, financial results, press releases | Daily | parsed → metadata → registry → chunks |
| 5 | Google Drive Knowledge Repo | Google Drive API | PDF/DOCX/PPTX/XLSX: FAQs, products, policies, compliance, research, training, circulars | Every 15 min | parsed → metadata → registry → chunks |

**Binding principles:** corporate filings are *knowledge documents* (registry → Qdrant later); market
data is **never** crawled and **never** served from Qdrant; all market providers implement
`MarketDataProvider`; no model weights run in-process.

## 4. What already exists (reuse — do not rebuild)

| Asset | Where | Reuse |
|---|---|---|
| Document Registry schema (`Document`, `DocumentChunk`, `DocumentVersion`, `DocumentAuditHistory`) | `app/db/models.py:111-161` | **High** — fields already match the roadmap `documents` table |
| Checksum + version + audit primitives | `app/db/seed.py:64-76` | Extract into a service |
| `MarketDataProvider` ABC + `MockMarketData` + `market_service.py` (Redis cache) | `app/adapters/*`, `app/services/market_service.py` | **High** — this is Source 2A's consumer |
| Adapter/factory + config + observability + Redis | `app/adapters/__init__.py`, `app/config.py`, `app/core/*` | High |
| Reserved Railway `worker` service | `infra/railway.md:11` | Instantiate it |
| Qdrant **validate-only** client | `app/adapters/qdrant_real.py` | **Boundary** — Phase 5 uses it; Phase 4 must not write |

## 5. Gap summary (build these)

P0 (spine): `IngestionSource` base + factory · DocumentRegistryService (dedup/version/register/audit) ·
Chunker · MetadataExtractor · Orchestrator (with a no-embed guard) · Worker + CLI.
P1: Parsers (HTML/PDF/DOCX/PPTX/XLSX) · Scheduler abstraction + cadences · `MarketDataProvider`
completion (`get_market_depth`/`get_option_chain`/`subscribe_ticks`) · `BA_MARKETDATA_PROVIDER` bugfix ·
env vars.
P2: `IngestionRun` bookkeeping table · admin ingestion endpoints · opt-in live source adapters ·
optional-dependency extras.

**Known Phase-3 debt fixed here:** `app/adapters/__init__.py:33` references `settings.marketdata_provider`,
which is undefined in `config.py` → `AttributeError` when `BA_USE_MOCKS=false`.

## 6. Build order

1. Config + `marketdata_provider` bugfix (add `BA_*` ingestion/chunking/cadence vars).
2. DB: `IngestionRun` table (+ optional `Document`/`DocumentChunk` columns) → Alembic `0002_phase4_ingestion` (additive, reversible).
3. `DocumentRegistryService` (dedup/version/register/audit); refactor `seed.py` onto it (keeps 20/20 green).
4. Chunker + MetadataExtractor + Parsers (deterministic, offline).
5. `IngestionSource` base + factory + six **fixture** sources.
6. Orchestrator: discover → parse → metadata → dedup → register → chunk. **Hard stop before embedding** (assert no Qdrant write).
7. Worker (`app/worker/runner.py`) + Scheduler abstraction (run-once now; cadences in config).
8. Market Data Provider Layer completion (extend ABC + mock; keep Redis branch).
9. Admin endpoints + `IngestionRun` visibility (audited, admin-gated).
10. Opt-in live source adapters (flag + optional-dep gated, default off).
11. Doc updates (this file, PHASE_STATUS, DECISIONS).

## 7. Files (preview)

**Create:** `app/ingestion/{__init__,base,registry_service,chunker,metadata,parsers,orchestrator,scheduler}.py` ·
`app/ingestion/sources/{__init__,mock_sources,broker_site,nse,bse,nalco_ir,gdrive}.py` ·
`app/ingestion/fixtures/…` · `app/worker/{__init__,runner}.py` ·
`app/api/routes_ingestion.py` · `app/schemas/ingestion.py` ·
`alembic/versions/0002_phase4_ingestion.py` ·
`tests/{test_ingestion_registry,test_chunker,test_ingestion_sources,test_orchestrator,test_market_provider_layer,test_scheduler_config}.py` ·
`infra/ingestion.md` · (optional) `requirements-ingest.txt`.

**Modify:** `app/config.py` · `app/adapters/base.py` (extend `MarketDataProvider`) ·
`app/adapters/mocks.py` · `app/adapters/__init__.py` (bugfix + ingestion factory) ·
`app/db/models.py` (+`IngestionRun`) · `app/db/seed.py` (use registry service) ·
`app/main.py` (include ingestion router; scheduler in worker only) · `docker-compose.yml` (+`worker`) ·
`infra/railway.md`.

## 8. New environment variables

`BA_INGEST_LIVE` (default `false`), `BA_CHUNK_SIZE`, `BA_CHUNK_OVERLAP`, `BA_MARKETDATA_PROVIDER` (bugfix),
`BA_BROKER_SITE_URL`, `BA_NSE_BASE_URL`, `BA_BSE_BASE_URL`, `BA_NALCO_IR_URL`, `BA_GDRIVE_FOLDER_ID`,
`BA_GDRIVE_CREDENTIALS_JSON`, and cadence vars `BA_INGEST_CRON_{BROKER,NSE,BSE,NALCO,GDRIVE}`.

## 9. Testing & rollback

**Testing:** all-offline deterministic suite (registry dedup/version, chunk counts, each mock source
discover+parse, orchestrator end-to-end producing chunks + audit **with no vector writes**, idempotent
re-ingest, market ABC extension, scheduler config parse). Live adapters skip-if-no-cred/flag. Keep
`pytest -q` green (20 existing + new) and mocks-first credential-free.

**Rollback:** additive/reversible migration; all live ingestion behind `BA_INGEST_LIVE=false`; the worker
is a **separate process** so the web request path and all six invariants are untouched (disabling the
worker = full rollback); `git revert` removes `app/ingestion/` + `app/worker/` cleanly.

## 10. Phase-4 → Phase-5 handoff contract

Phase 4 **produces**, in PostgreSQL:
- `Document` rows: `source, url, company, filing_type, filing_date, document_version, checksum` (+ `title`).
- `DocumentChunk` rows: `document_id, chunk_index, text, lang`.
- `DocumentVersion` + `DocumentAuditHistory` rows (dedup/version trail).

Phase 5 **consumes** those chunks → dense embed (Ollama Cloud · embeddinggemma) + native sparse (BM25/IDF)
→ upsert into Qdrant `brokerage_kb` with an **FK-only + retrieval-filter** payload. Phase 4 writes **no**
vectors. See [PHASE_5_KICKOFF.md](PHASE_5_KICKOFF.md).

## Phase-numbering correction

The roadmap numbering is authoritative:
**Phase 4 = Data Ingestion Layer · Phase 5 = Embedding Pipeline · Phase 6 = RAG System · Phase 7 = Multilingual Layer.**
Earlier project docs labeled "Real Vendor Adapters" as *Phase 4* and folded ingestion into *Phase 5/6*.
That drift is corrected in [PHASE_STATUS.md](PHASE_STATUS.md) and [ROADMAP.md](ROADMAP.md). "Real vendor
adapters" is a **cross-cutting wiring workstream** (still tracked in [NEXT_PHASE_PLAN.md](NEXT_PHASE_PLAN.md)
§C), not a roadmap phase.
