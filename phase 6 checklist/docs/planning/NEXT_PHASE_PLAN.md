# Next-Phase Plan — what to build next, and how

> **For the agent picking up this project:** read [PHASE_STATUS.md](PHASE_STATUS.md) first, then pick a
> workstream below. Each workstream states its **gate** (what must be true to start), concrete
> **file-level steps**, **acceptance criteria**, and **risks**. Respect the
> [invariants](PHASE_STATUS.md#load-bearing-invariants-do-not-break-when-extending).

> **⚠️ Numbering note (2026-06-24).** This file pre-dates the roadmap-numbering correction and uses
> *workstream* labels. Map them to roadmap phases as follows: **Workstream A (ingestion) → Phase 4
> Data Ingestion Layer** (now superseded by the dedicated, design-approved [PHASE_4_PLAN.md](PHASE_4_PLAN.md),
> which scopes ingestion to *stop before embeddings*); **embed → upsert to Qdrant → Phase 5
> Embedding Pipeline** ([PHASE_5_KICKOFF.md](PHASE_5_KICKOFF.md)); **Workstream C "real vendor adapters"
> is a cross-cutting wiring workstream, NOT roadmap Phase 4.** Use `PHASE_4_PLAN.md` /
> `PHASE_5_KICKOFF.md` as the current source of truth; the workstreams below remain a useful catalog.

## Choose by gate

```
Need ZERO credentials?   → A (ingestion worker skeleton)   or   B (widget package)
Have ONE vendor key?     → C, in order: Sarvam → Ollama embed → Qdrant → reranker → Gemma → TrueData
Have owner decisions?    → D (production hardening)
```

Recommended sequence: **A → C (vendor by vendor) → B → D.** Workstream A makes the real Qdrant path
meaningful; doing it first means each real adapter in C has data to operate on.

---

## Workstream A — Ingestion / embedding worker  ⛔ (no credentials needed to scaffold)

**Objective:** a background pipeline that turns registered documents into Qdrant vectors:
`document → chunk → embed → upsert(payload = FK only)`. This is the missing half of RAG (retrieval
exists; ingestion does not).

**Gate:** none to build the **skeleton against mocks**. Real embedding/upsert needs Ollama + Qdrant
(Workstream C), but the worker, chunker, and orchestration can be built and tested now.

**Steps**
1. New module `apps/backend/app/worker/` with:
   - `chunker.py` — split `Document` text into `DocumentChunk` rows (size/overlap configurable).
   - `ingest.py` — orchestrate: load unindexed docs → chunk → `embedding.embed()` → `vector_store.upsert()`
     → write a `DocumentAuditHistory("reindexed")` row.
   - `runner.py` — a CLI entry (`python -m app.worker.runner`) and/or a Railway `worker` service command.
2. Extend the `VectorStore` interface in `adapters/base.py` with `upsert(chunks)` and implement it in
   `MockVectorStore` (in-memory) so the worker is testable without Qdrant.
3. Add an admin trigger: `POST /api/v1/admin/documents/{id}/reindex` (audited) for manual ingestion.
4. Reserve `BA_CHUNK_SIZE`, `BA_CHUNK_OVERLAP` in `config.py`.

**Acceptance**
- Seeding a new `Document` + running the worker produces `DocumentChunk` rows and (mock) vectors; a
  follow-up `/chat` retrieves and cites the new doc.
- New tests in `tests/test_worker.py` (chunk counts, idempotent re-ingest, audit row written).

**Risks:** chunk strategy affects retrieval quality — keep it config-driven and re-runnable
(checksum-based skip already modeled via `document_versions`).

---

## Workstream B — Standalone embeddable widget package  ⛔ (no credentials needed)

**Objective:** ship the assistant as a single embeddable script (`<script src=...>` + one snippet) so a
brokerage can drop it on any site — independent of the Next.js app. `packages/widget/` is an empty
placeholder today.

**Steps**
1. Scaffold `packages/widget/` (Vite or esbuild) producing a self-contained `brokerassist-widget.js`.
2. Port `apps/frontend/components/Assistant.jsx` + `lib/api.js` + `lib/i18n.js` into framework-light
   form (web component or vanilla) reading config from data attributes
   (`data-widget-key`, `data-api-base`, `data-lang`).
3. Mount into a shadow DOM so host-page CSS can't bleed in; expose the same `ba-ask` event hook.
4. Provide an embed snippet + a static demo `index.html`.

**Acceptance:** the built script, dropped into a bare HTML page served from an allowlisted Origin,
creates a session and returns a cited answer (same flow verified for the Next.js widget in TESTING.md).

**Risks:** CSS isolation and CSP on host sites — shadow DOM + no inline eval.

---

## Workstream C — Real vendor adapters (Phase 4)  ⛔ ⚠️ (needs credentials, one vendor at a time)

**Objective:** flip `BA_USE_MOCKS=false` and implement the real adapters behind the **existing**
interfaces in `adapters/base.py`. Callers do not change (ADR-001). The factory in
`adapters/__init__.py` currently raises `NotImplementedError` for each.

**General method (per vendor):**
1. Implement the real class (e.g. `adapters/sarvam.py`) against the ABC.
2. Wire it into the factory `get_*()` for the non-mock branch.
3. Add the vendor key(s) to `config.py` (`BA_*`) and `.env.example`.
4. Add a contract test that runs against the mock by default and the real vendor when keys are present
   (skip-if-no-key), so CI stays credential-free.
5. Update the [readiness scorecard](../../deliverables/phase_2/discovery/03_readiness_scorecard.md) row
   from ⚠️ to ✅.

**Recommended order (lowest blast radius first):**

| Order | Adapter | Interface | Vendor | Env | Unblocks |
|---|---|---|---|---|---|
| 1 | Language | `LanguageProvider` | Sarvam AI | `BA_SARVAM_API_KEY` | real EN/HI/TA detect + translate |
| 2 | Embedding | `EmbeddingProvider` | Ollama Cloud · embeddinggemma | `BA_OLLAMA_*` | real vectors (pairs with Workstream A) |
| 3 | Vector store | `VectorStore` | Qdrant | `BA_QDRANT_URL`, `BA_QDRANT_API_KEY` | real hybrid retrieval; flip `qdrant_create_if_missing` + set `BA_QDRANT_DENSE_DIM` |
| 4 | Re-ranker | `ReRanker` | hosted cross-encoder (bge) | `BA_RERANKER_URL` | real Top-5 precision |
| 5 | LLM | `LLM` | Ollama Cloud · Gemma | `BA_OLLAMA_*` | real grounded generation |
| 6 | Market data | `MarketDataProvider` | TrueData | market creds, `BA_MARKETDATA_PROVIDER` | live quotes |

**Qdrant specifics:** `adapters/qdrant_real.py` already validates the collection contract (dense +
native sparse, **FK-only payload**). For real use: provide `BA_QDRANT_DENSE_DIM` (match the embedding
model), set `BA_QDRANT_CREATE_IF_MISSING=true` for first-time creation, then run Workstream A to
populate.

**Acceptance:** with all six wired and `BA_USE_MOCKS=false`, the same E2E in TESTING.md passes against
real services; a HI/TA question now returns a *genuinely translated* answer (the one behaviour the mock
can't do).

**Risks:** Tamil finance NLP quality (Phase 0's top risk) — validate Sarvam HI/TA translations against
seeded answers before trusting generation; cost — confirm `BA_TENANT_DAILY_QUOTA` and budget caps
(DECISIONS) before exposing real LLM calls publicly.

---

## Workstream D — Production hardening & launch (Phase 7)  ⛔ ⚠️ (needs owner decisions)

**Objective:** make the system safe and operable for real tenants.

**Steps (each gated on a decision in [DECISIONS_AND_OPEN_ITEMS.md](DECISIONS_AND_OPEN_ITEMS.md)):**
1. Set SLOs from the latency/availability/volume TBDs; add load tests.
2. Implement data **retention/deletion** jobs (sessions, logs, analytics) per the residency decision;
   choose Qdrant/DB region accordingly.
3. **Source-authority precedence** (open ADR-009) — encode conflict resolution (NSE vs BSE vs IR vs
   broker site) into retrieval/citation ranking.
4. Secrets management on Railway (open ADR-010); rotate all dev secrets.
5. Multi-tenant onboarding flow (admin UI for tenant + key + allowlist provisioning).
6. Legal/compliance review of disclaimers and algo content (SEBI/NSE).

**Acceptance:** a load test meets the agreed SLOs; a documented runbook exists; legal sign-off recorded.

---

## Definition of done (any workstream)

- [ ] Code follows the existing patterns (adapters, services, audited admin writes).
- [ ] No invariant broken (see PHASE_STATUS).
- [ ] Tests added; `pytest -q` green; mocks-first still runs credential-free.
- [ ] [PHASE_STATUS.md](PHASE_STATUS.md) row(s) updated ⛔/⚠️ → ✅.
- [ ] Any new decision recorded in [DECISIONS_AND_OPEN_ITEMS.md](DECISIONS_AND_OPEN_ITEMS.md) (close the
      matching open ADR).
