# Phase 5 — Embedding Pipeline (kickoff brief for structuring)

> ✅ **IMPLEMENTED MOCKS-FIRST (2026-06-25).** This brief has been executed. Code:
> `app/services/embedding_pipeline.py` (orchestration + sparse encoder + startup check),
> `app/services/metadata_contract.py` (canonical enums + FK-only payload),
> `app/adapters/ollama_cloud.py` (real embeddinggemma, credential-gated),
> `app/adapters/qdrant_real.py` (dual-vector `brokerage_kb` lifecycle + upsert, dynamic dim),
> `app/services/document_registry_service.py`, `app/worker/embed_runner.py`. Tests:
> `tests/test_phase5_*.py` (31 tests; 51 total green). Run: `python -m app.worker.embed_runner --seed --once`.
> Decisions locked: P5-D1/D2/D3 + ADR-011/012/013 closed in [DECISIONS_AND_OPEN_ITEMS.md](DECISIONS_AND_OPEN_ITEMS.md).
> Live path still gated on rotated Ollama/Qdrant credentials (and a real Phase-4 corpus).


> **Purpose of this file:** give the next agent everything needed to **structure Phase 5** the same way
> Phase 4 was structured — roadmap requirements extracted, current-code reuse/gaps mapped, the
> handoff contract from Phase 4 stated, invariants restated, and the open questions surfaced.
> **This is a planning scaffold, not an implementation.**
>
> **Source of truth:** roadmap pp. 16–19 (Phase 5 — Embedding Pipeline). Phase 6 (RAG, pp. 20–22)
> is the *consumer* of Phase 5 and is shown only for context.
>
> **Hard dependency:** Phase 5 consumes the output of [PHASE_4_PLAN.md](PHASE_4_PLAN.md). If Phase 4
> is not yet implemented, Phase 5 can be **structured** now but cannot be **built/verified end-to-end**
> until Phase 4 produces `DocumentChunk` rows.

---

## 1. Phase 5 goal (roadmap)

Turn the Phase-4 `DocumentChunk` rows into vectors in Qdrant: **dense embedding (Ollama Cloud ·
embeddinggemma) + native sparse (BM25/IDF)** written into a **dual-vector `brokerage_kb` collection**,
with a foreign-key-only + retrieval-filter payload. No model weights run in-process.

## 2. Roadmap requirements (extracted, pp. 16–19)

**Embedding model**
- `embeddinggemma` — multilingual (EN/HI/TA) embedding model served by Ollama Cloud. No local weights.

**Dimension handling (binding)**
- Detect the dense dimension **dynamically** from a probe embedding — `embedding_dimension = ollama_cloud.embeddings("embeddinggemma").dimension`.
- **Never hardcode** the vector dimension. The app must not assume a fixed vector size.
- Qdrant collection dimension is generated dynamically.

**Collection: `brokerage_kb` (dual-vector)**
- Named **dense** vector: `size = detected dimension`, `distance = COSINE`.
- Native **sparse** vector: `BM25 / IDF` (`SparseVectorParams(modifier=Modifier.IDF)`) — **no Elasticsearch**.

**Collection initialization (a STARTUP responsibility, not ingestion)**
1. Configure the Ollama Cloud embedding model (embeddinggemma).
2. Detect embedding dimension automatically.
3. Connect to Qdrant.
4. Check whether `brokerage_kb` exists.
5. If absent → create with dense (detected dim) + native sparse (BM25/IDF).
6. If present → validate dense dim matches the model **and** sparse is configured.
7. **Stop startup** if dimensions or vector config do not match.
8. Mark embedding service ready.

**Validation**
- *At startup:* model reachable, dimension detected, collection exists with dense+sparse, dense dim matches.
- *Before indexing:* vector compatibility (dense + sparse), metadata integrity, collection availability.
- *On mismatch:* log error, **stop ingestion**, notify administrator. (Prevents corrupted vector storage.)

**Qdrant payload — corrected contract (roadmap p. 19)**
- **Stored in Qdrant payload:** `Document ID`, `Chunk ID` (FKs) **+ retrieval filters**: `Language`,
  `Company`, `Filing Type`, `Date`.
- **Resolved from PostgreSQL at citation time (never stored in Qdrant):** `source`, `url`,
  `document_version`, `checksum`, any other citation metadata.

**Architecture principle:** collection creation is a startup responsibility; document ingestion must
**never** create collections. No embedding/reranker weights run on FastAPI/Railway — embeddings are
served by Ollama Cloud; reranking by a hosted cloud endpoint.

## 3. Current code — reuse vs gaps for Phase 5

| Asset | Where | State for Phase 5 |
|---|---|---|
| Qdrant client + collection **validation** | `app/adapters/qdrant_real.py` | ✅ reuse. Already validates dense+sparse + payload contract; **validate-only (no writes)**. Phase 5 adds dynamic-dim **creation** + **upsert**. |
| `PAYLOAD_CONTRACT = {"document_id","chunk_id"}` | `app/adapters/qdrant_real.py:11` | 🔧 **expand** to add filter fields `{language, company, filing_type, date}` per roadmap p. 19. |
| Collection name | `app/config.py` → `qdrant_collection="brokerassist_knowledge"` | ⚠️ roadmap calls it **`brokerage_kb`** — reconcile (open item below). |
| Dim config | `qdrant_dense_dim: int\|None=None`, `qdrant_create_if_missing=False` | 🔧 Phase 5 replaces "hardcoded dim + create flag" with **dynamic probe detection**. |
| `VectorStore` ABC | `app/adapters/base.py:30` | 🔧 has only `hybrid_search`; **add `upsert(chunks, vectors, payloads)`**. |
| `MockEmbedding` (16-dim hash vector) | `app/adapters/mocks.py:66` | ✅ reuse for **offline** Phase 5 tests of the upsert path. |
| `get_embedding()` / `get_vector_store()` | `app/adapters/__init__.py` | 🔧 real branches raise `NotImplementedError` — wire real Ollama embeddinggemma + real Qdrant upsert. |
| `DocumentChunk.lang`, `Document.{company,filing_type,filing_date}` | `app/db/models.py` | ✅ map directly to the Qdrant **retrieval-filter** payload fields. |
| Worker orchestrator (Phase 4) | `app/worker/` (to be built in P4) | 🔧 Phase 5 **adds the embed+upsert stage** to the same worker, after chunking. |

## 4. Phase-4 → Phase-5 handoff contract

**Input to Phase 5** (produced by Phase 4, in PostgreSQL): `DocumentChunk(document_id, chunk_index,
text, lang)` + `Document(source, url, company, filing_type, filing_date, document_version, checksum)`.

**Phase 5 stage** (extends the Phase-4 worker, after chunking):
`for each unembedded chunk → dense = embeddinggemma.embed(text); sparse = bm25(text) →
validate dims → upsert(brokerage_kb, id=chunk_id, vectors={dense,sparse},
payload={document_id, chunk_id, language, company, filing_type, date}) →
audit "indexed"`. Citations still resolve from PostgreSQL (ADR-002 unchanged).

## 5. Invariants Phase 5 must preserve

1. Citations resolve from **PostgreSQL**, never Qdrant (payload = FKs + filters only). *(ADR-002)*
2. Market data never comes from the vector store. *(ADR-004)*
3. **No model weights in-process** — embeddings via Ollama Cloud only. *(ADR-001)*
4. Collection creation is a **startup** responsibility; ingestion never creates collections.
5. **Never hardcode the embedding dimension** — detect dynamically.
6. **Mocks-first must keep working** — the embed+upsert path must run against `MockEmbedding` +
   an in-memory/mock vector store with zero credentials.

## 6. Open questions to resolve when structuring Phase 5

1. **Collection name** — adopt roadmap `brokerage_kb`, or keep code's `brokerassist_knowledge` and
   alias? (Recommend: rename to `brokerage_kb` to match roadmap; one config change.)
2. **Sparse vector generation** — use Qdrant native BM25/IDF server-side, or compute sparse vectors
   client-side? (Roadmap says native Qdrant sparse.)
3. **Mocks-first for embeddings** — ship a real `OllamaEmbeddingAdapter` now (needs `BA_OLLAMA_*`
   creds), or build the full embed+upsert path against `MockEmbedding` + a real-Qdrant-optional store,
   credential-gated like Phase 4's live sources? (Recommend the latter to preserve mocks-first.)
4. **Startup dim-detection placement** — web process, worker, or a one-shot init job? Must run before
   first ingestion and must be able to **stop startup** on mismatch.
5. **Re-embedding / backfill** — when chunks change (Phase-4 versioning), how are stale vectors
   replaced (delete-by-FK then re-upsert)?
6. **Batching & rate/cost** — embedding call batching and per-tenant cost caps (ties to budget TBD).
7. **`qdrant_dense_dim` config** — remove/deprecate the hardcoded-dim field in favor of dynamic
   detection, keeping an optional assertion override.

## 7. How to structure Phase 5 (suggested method for the next agent)

Mirror the Phase-4 process: (1) re-read roadmap pp. 16–19; (2) confirm Phase-4 output exists (or note
the dependency); (3) produce a Phase-5 plan with the same sections as [PHASE_4_PLAN.md](PHASE_4_PLAN.md)
— goal, locked decisions, gap analysis, build order, files, env vars, testing, rollback, and the
**Phase-5 → Phase-6 handoff** (hybrid retrieval consumes `brokerage_kb`); (4) keep all six invariants
and mocks-first; (5) stop at an approval gate before coding.

**Phase-6 preview (consumer, do not build in Phase 5):** Branch-B RAG does query translation → embed →
dense+sparse hybrid retrieval over `brokerage_kb` with metadata filters applied **at retrieval** → RRF →
Top-20 → cross-encoder rerank → Top-5 → Gemma → translate → citations from PostgreSQL (roadmap pp. 20–22).
