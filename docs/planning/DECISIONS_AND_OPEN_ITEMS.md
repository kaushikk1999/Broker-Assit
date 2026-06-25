# Decisions & Open Items

A consolidated register so an agent can tell, at a glance, **what is settled** (and must be respected)
versus **what is still open** (and gates the next phase). Sources: the Phase 2 decisions log, the ADR
log, and the information inventory under `deliverables/phase_2/discovery/`.

---

## Accepted decisions (respect these)

### Product / program (Phase 0–2 decisions log)
| # | Decision | Value |
|---|---|---|
| D1 | Frontend strategy | Port Phase 1 prototype → Next.js (App Router) + extract embeddable widget |
| D2 | Repo / deploy | Monorepo, multi-service on Railway |
| D3 | Build scope | NALCO knowledge-RAG pilot thin-slice first; market + worker stubbed |
| D4 | Vendor readiness | Mocks/stubs first behind clean interfaces; wire real vendors later |
| D5 | Tenant model | Multi-tenant SaaS (public widget key + domain allowlist) |
| D6 | Audience | B2B brokerages (primary); end-investors (secondary) |
| D7 | Languages | EN, HI, TA; query translated to EN before retrieval |
| D8 | Local DB | SQLite (dev) / PostgreSQL (prod), same SQLAlchemy models |
| D9 | Citations | Resolved from PostgreSQL registry; Qdrant payload = FKs only |

### Architecture (accepted ADRs — these are the code's spine)
| ADR | Decision |
|---|---|
| ADR-001 | Mocks-first provider interfaces (every vendor behind an ABC + factory by `BA_USE_MOCKS`) |
| ADR-002 | Citations resolved from PostgreSQL, **not** the vector store |
| ADR-003 | SQLite for dev, PostgreSQL for prod (one model layer) |
| ADR-004 | Intent-routing fork **before** retrieval (market never touches Qdrant) |
| ADR-005 | Abuse/cost control **before** any model call |

### Phase 4 — Data Ingestion Layer (design-approved 2026-06-24; **implemented 2026-06-25**; see [PHASE_4_PLAN.md](PHASE_4_PLAN.md))
| # | Decision | Value |
|---|---|---|
| P4-D1 | Pipeline seam | **Stop at chunking** — Phase 4 produces `DocumentChunk` rows; embeddings/Qdrant writes are Phase 5 |
| P4-D2 | Live sources this phase | **Fixtures + opt-in live adapters** — full pipeline on offline fixtures; real crawler/NSE/BSE/Drive gated behind `BA_INGEST_LIVE` (default off) + optional-dep extras |
| P4-D3 | Scheduling | **Run-once commands + worker + config cadences** — cron in the Railway worker only, never the web process |
| P4-D4 | Registry write-service split | `app/ingestion/registry_service.py` (dedup/version/register/audit, **full SHA-256** checksum) owns Document/Version/Audit rows; the orchestrator owns chunk writes. Read-side lookups stay in `services/document_registry_service.py`. |
| P4-D5 | No-vector guard | The orchestrator imports **no** vector store / embedding provider; a test (`test_orchestrator.test_orchestrator_writes_no_vectors`) asserts the writable store count stays 0 after a run — the structural enforcement of P4-D1. |
| P4-D6 | Migration guard | `0001_initial` builds the baseline via `create_all` over *current* metadata, so `0002_phase4_ingestion` is **inspector-guarded** (no-op when `ingestion_runs` already exists) and reversible — safe on both fresh and pre-existing 0001 databases. |
| P4-D7 | Canonical metadata at ingest | `metadata.extract` guarantees a **canonical `filing_type`** (taxonomy + keyword inference + safe default) and supported language, so Phase 5's strict FK-payload build never rejects an ingested chunk. |

### Phase 6 — RAG System (implemented 2026-06-25)
| # | Decision | Value |
|---|---|---|
| P6-D1 | Hybrid fusion location | **Server-side RRF in Qdrant** via the Query API (`query_points` with dense + sparse prefetches, each carrying the metadata filter, fused with `Fusion.RRF`). Mock store mirrors this in Python. |
| P6-D2 | Citation invariant on real read | Qdrant read returns **FKs + score only**; chunk text + citations are **hydrated from PostgreSQL** (`rag_pipeline._hydrate_text`). Honors ADR-002 on the live path. |
| P6-D3 | Sparse query/index parity | Query sparse vector reuses **the same `embedding_pipeline.sparse_encode`** used at ingestion. |
| P6-D4 | Metadata filters | Applied **at retrieval on both branches**, canonicalized by a shared `metadata_contract.normalize_filters`. Only payload fields filter (`company`, `filing_type`, `language`, `date`); `source` is PostgreSQL-only and is dropped. |
| P6-D5 | Language retrieval filter | **OFF by default** (`BA_RETRIEVAL_LANGUAGE_FILTER=false`): the query is translated to English and embeddinggemma is multilingual, so a language filter would wrongly exclude EN docs. |
| P6-D6 | Auto filter derivation | Intent router derives a **company filter only** (high-precision, pilot = NALCO). `filing_type` is **not** auto-derived (small corpus + taxonomy overlap → over-filtering risk); explicit module filters still honored. |
| P6-D7 | Query expansion | Deterministic, dependency-free acronym/synonym expansion for **retrieval recall only**; reranking + generation use the original question. Toggle `BA_QUERY_EXPANSION_ENABLED`. |
| P6-D8 | Reranker resilience | Hosted cross-encoder; on outage it **degrades to the incoming RRF order** (`BA_RERANK_FALLBACK_ENABLED=true`). Reranker is precision, not a correctness gate. |
| P6-D9 | Sarvam pulled into Phase 6 | The real **Sarvam detect/translate** adapter was built now (owner decision) behind `get_language()`; the rest of Phase 7 (transliteration / STT / TTS / UI) is unchanged. |
| P6-D10 | Hosted-model constraint preserved | Reranker + Gemma generation + Sarvam are all **remote calls behind ABCs**; no model weights run in the FastAPI/Railway process. |

### Phase-numbering correction (2026-06-24)
Roadmap numbering is authoritative: **Phase 4 = Data Ingestion · Phase 5 = Embedding · Phase 6 = RAG ·
Phase 7 = Multilingual.** "Real vendor adapters" is a cross-cutting wiring workstream
([NEXT_PHASE_PLAN.md](NEXT_PHASE_PLAN.md) §C), **not** a roadmap phase. Updated in
[PHASE_STATUS.md](PHASE_STATUS.md) and [ROADMAP.md](ROADMAP.md).

> These map 1:1 to the [invariants](PHASE_STATUS.md#load-bearing-invariants-do-not-break-when-extending).
> Changing one means writing a superseding ADR, not a silent edit.

---

## Open ADRs (write before production)

| ADR | Question | Blocks |
|---|---|---|
| ADR-006 | Qdrant hosting — Qdrant Cloud vs Railway-hosted | Workstream C-3 |
| ADR-007 | Re-ranker provider / endpoint — **partially addressed (Phase 6):** a generic hosted cross-encoder adapter (`adapters/reranker_cloud.py`) with a configurable request/response contract + RRF fallback is implemented; the specific production vendor/endpoint is still open. | Workstream C-4 |
| ADR-008 | Market-data vendor + licensing (roadmap: TrueData primary) | Workstream C-6 |
| ADR-009 | Source-authority precedence on conflict (NSE/BSE/IR/site) | Workstream D-3 |
| ADR-010 | Secrets management on Railway | Workstream D-4 |
| ~~ADR-011~~ | **Resolved (Phase 5):** adopted canonical `brokerage_kb` (env `BA_QDRANT_COLLECTION_NAME`) with `BA_QDRANT_COLLECTION` kept as a backward-compat alias. | closed |
| ~~ADR-012~~ | **Resolved (Phase 5):** `PAYLOAD_CONTRACT` expanded to `{document_id, chunk_id, language, company, filing_type, date}`; citation fields stay PostgreSQL-only. | closed |
| ~~ADR-013~~ | **Resolved (Phase 5):** dynamic probe-based dimension detection (`EmbeddingProvider.probe_dimension()`); `BA_QDRANT_DENSE_DIM` superseded by optional `BA_EMBEDDING_DIMENSION_OVERRIDE` (alias retained). | closed |

### Phase 5 — Embedding Pipeline (implemented mocks-first 2026-06-25)
| # | Decision | Value |
|---|---|---|
| P5-D1 | Phase-4 gap | **Build Phase 5 mocks-first now** against the existing `DocumentChunk` contract; data-agnostic, backfills when Phase 4 lands |
| P5-D2 | Naming | **Adopt roadmap canon (`brokerage_kb`, `dense`/`sparse`, `BA_OLLAMA_CLOUD_*`) + keep backward-compat aliases** |
| P5-D3 | Startup policy | **Conditional fail-fast, create=false default** — fail fast only when a real Qdrant/Ollama is configured and mismatched; mocks mode always boots; collection auto-create opt-in |

---

## Open inputs (TBD — owner confirmation needed)

From `01_information_inventory_filled.md`. **None block the mocks pilot; all block production launch.**

| Input | Proposed default (not yet confirmed) | Gates |
|---|---|---|
| Primary success metrics | support-deflection %, cited-answer rate, EN/HI/TA coverage, demo→lead | Phase 7 |
| Launch scope | multi-tenant onboarding + real vendors + worker + market data | Phase 7 |
| Expected volumes | roadmap 100+ concurrent; need avg/peak/burst | SLOs, scaling |
| Latency target | market < 800 ms; knowledge < 4 s p95 | SLOs |
| Availability | 99.5% pilot | SLOs |
| RPO / RTO | owner to set (registry is the durable asset) | DR plan |
| Budget ceiling + cost caps | needed to bound Ollama/Sarvam/market spend | Workstream C exposure |
| Data retention / deletion | sessions/logs/analytics periods + deletion workflow | Workstream D-2 |
| Data residency | India residency likely → constrains Qdrant/DB region | Workstream C-3, D-2 |
| Compliance / legal sign-off | disclaimers in place; legal review pending | Phase 7 launch |
| Operational ownership | named owners (arch/ops/security/vendors) | launch |

---

## How to use this register

- **Before building:** check the workstream's gate here. If it points to an open ADR or TBD input,
  either resolve it with the owner or build only the part that doesn't depend on it (e.g. scaffold the
  worker against mocks while Qdrant hosting is undecided).
- **After deciding:** record the decision (new D# or close the open ADR), then flip the matching row in
  [PHASE_STATUS.md](PHASE_STATUS.md) and the
  [readiness scorecard](../../deliverables/phase_2/discovery/03_readiness_scorecard.md).
