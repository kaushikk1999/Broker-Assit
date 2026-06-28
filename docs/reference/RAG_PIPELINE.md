# RAG Pipeline — deep dive

The knowledge branch (Branch B of the intent router) is the heart of BrokerAssist. This is the
stage-by-stage reference for `apps/backend/app/services/rag_pipeline.py` and the adapters it drives.

![RAG pipeline](../diagrams/rag-pipeline.svg)

*Raster copy: [`diagrams/rag-pipeline.png`](../diagrams/rag-pipeline.png)*

---

## When it runs

`POST /chat` first calls `intent_router.classify()`. If the message is **not** a market lookup
(market keyword **and** a known symbol), it enters this pipeline via `handle_knowledge(message,
user_lang, db, filters=...)`. Phase 6: `classify()` returns the roadmap intent taxonomy
(`disclosure | navigation | faq | algo`) **and** a derived metadata filter (a `company` filter when a
company is detected — high precision, pilot = NALCO), which `/chat` passes into `handle_knowledge`.
The `/search` and `/filings` module endpoints reuse the same function (`/filings` passes a `company`
filter when provided; `source` is PostgreSQL-only and is **not** a Qdrant retrieval filter).

---

## The eight stages

| # | Stage | Code | Adapter (prod vendor) |
|---|---|---|---|
| 1 | Detect language | `language.detect()` (only if needed) | `LanguageProvider` (Sarvam) |
| 2 | Translate query → English | `language.translate(target="en")` | `LanguageProvider` (Sarvam) |
| 2b | **Expand query (recall)** | `query_expansion.expand_query()` | — (deterministic, in-process) |
| 3 | Embed the expanded query | `embedding.embed()` | `EmbeddingProvider` (embeddinggemma) |
| 4 | Hybrid retrieve (dense + sparse, filtered) | `store.hybrid_search()` | `VectorStore` (Qdrant) |
| 5 | RRF fuse → Top-20 (server-side in Qdrant) | `hybrid_search` / Qdrant Query API | `VectorStore` |
| 5b | **Hydrate chunk text from PostgreSQL** | `rag_pipeline._hydrate_text()` | PostgreSQL |
| 6 | Cross-encoder rerank → Top-5 (+ relevance gate) | `reranker.rerank()` + `_is_relevant()` | `ReRanker` (hosted bge) |
| 7 | Generate grounded answer | `llm.generate()` | `LLM` (Gemma · Ollama Cloud) |
| 8 | Translate back + resolve citations | `language.translate()` + Postgres lookup | `LanguageProvider` + PostgreSQL |

### 1–2. Language detect & query translation
The query is **translated to English before retrieval** (`query_en = translate(message, "en", lang)`
when `user_lang != "en"`). This is the key move that makes Hindi/Tamil recall work against an
English-first index. In the mock (`adapters/mocks.py`), `MockLanguage.translate` maps HI/TA finance
terms (नालको→nalco, லாभांश/டிவிடெண்ட்→dividend, …) to English; Sarvam does this for real in production.

### 2b. Query expansion (recall)
`query_expansion.expand_query(query_en)` appends canonical domain synonyms for any known terms
(NALCO → "national aluminium", "result(s)" → "quarterly results", "algo" → "algorithmic trading",
white-box/black-box, …). It is **deterministic and dependency-free** (no vendor), a **no-op for
queries with no known terms** (e.g. greetings — which keeps the relevance gate honest), and is used
**only for retrieval** — reranking and generation use the original question, so precision is unaffected.
Toggle with `BA_QUERY_EXPANSION_ENABLED` (default on).

### 3. Embedding
`embedding.embed(query_retrieval)` returns a dense vector for the expanded query. The mock returns a
deterministic hash-based vector; production uses Ollama Cloud · embeddinggemma. **No model weights run
in-process** — it's a remote call behind the adapter.

### 4–5. Hybrid retrieval + RRF
`store.hybrid_search(query_retrieval, query_vec, top_k=BA_RETRIEVE_TOP_K, filters=...)` runs **two**
retrievals and fuses them with **Reciprocal Rank Fusion** (`rrf_score += 1/(BA_RRF_K+rank)`, default
`BA_RRF_K=60`):
- **Dense** — semantic similarity (mock proxy = token-overlap Jaccard).
- **Sparse** — keyword/lexical (mock = BM25-lite with IDF over the seeded chunks).

Filters are **canonicalized once** (`metadata_contract.normalize_filters` — only payload fields
`company`/`filing_type`/`language`/`date` survive; `language` is dropped unless
`BA_RETRIEVAL_LANGUAGE_FILTER` is on) and applied **at retrieval on both branches** (not post-hoc).
Output: the fused **Top-20** candidate chunks.

In production, `adapters/qdrant_real.QdrantReadStore` issues a single Qdrant **Query API** call with a
dense prefetch + a native-sparse prefetch (each carrying the metadata `Filter`), fused **server-side**
with `Fusion.RRF`. The query's sparse vector reuses the **same `sparse_encode`** used at ingestion, so
query/index parity holds. The FK-only payload means the fused result carries `(document_id, chunk_id)`
references, **not** citation text.

### 5b. PostgreSQL text hydration
Because the real Qdrant read returns FKs only, `rag_pipeline._hydrate_text(db, candidates)` loads each
chunk's text from PostgreSQL (`DocumentChunk.text`) before reranking — preserving the citation
invariant (Qdrant payload = FKs; text + citations come from PostgreSQL). The mock store returns text
inline, so hydration is a no-op there.

### 6. Rerank + relevance gate
`reranker.rerank(query_en, candidates, top_k=BA_RERANK_TOP_K)` re-scores the Top-20 with a
cross-encoder and keeps the **Top-5**. The mock is a query/chunk token-overlap proxy; production uses a
**hosted** cross-encoder (`adapters/reranker_cloud.HostedReRanker`, e.g. BAAI/bge-reranker) — a remote
call, no weights in-process. If the endpoint is unreachable it **degrades to the incoming RRF order**
(`BA_RERANK_FALLBACK_ENABLED`, default on): precision dips but the answer still returns.

Then the **relevance gate** (`_is_relevant`) checks whether the query's content tokens (stop-words
removed) actually overlap the retrieved chunks. **If nothing meaningfully overlaps** (chit-chat,
off-topic), the pipeline returns a localized **fallback message with NO citations** rather than citing
unrelated filings — `debug.grounded = false`. This is what keeps the assistant honest on small talk.

### 7. Generation
`llm.generate(query_en, context=[top-5 chunk texts])` produces the English answer **grounded only in
the Top-5 context**. The mock LLM is deliberately **non-hallucinating** — it returns the top retrieved
chunk verbatim, so the answer always aligns with a real citation. Production uses Gemma (Ollama Cloud).

### 8. Translate back + citations
The English answer is translated back to `user_lang` (mock has canned HI/TA translations for the
seeded NALCO answer; Sarvam translates anything in prod). **Citations are then resolved from
PostgreSQL** — for each of the top chunks, `db.get(Document, document_id)` supplies `source`, `title`,
`url`, `filing_date`. **Citations never come from the vector store** (ADR-002).

---

## Output

`handle_knowledge` returns `{answer, citations, debug}`, which the route wraps in a `ChatResponse`
with `branch:"knowledge"`, the routed `intent`, and the disclaimer *"Informational only — not
investment advice."* (`DISCLAIMER`). Up to 3 citations are surfaced.

---

## Tunables (`config.py`)

| Setting | Default | Effect |
|---|---|---|
| `BA_RETRIEVE_TOP_K` | 20 | Candidate pool after RRF |
| `BA_RERANK_TOP_K` | 5 | Context window after rerank |
| `BA_SUPPORTED_LANGUAGES` | `en,hi,ta` | Languages eligible for detect/translate |

---

## Invariants (do not break)

1. **Translate the query to English *before* retrieval** — multilingual recall depends on it.
2. **Filters applied at retrieval**, then RRF, then rerank — never filter after generation.
3. **Relevance gate before citing** — no citations on ungrounded answers.
4. **Citations resolve from PostgreSQL**, FK-only payload in Qdrant.
5. **Generation is grounded** strictly in the reranked Top-5 context.

---

## Mock vs production parity

The mock implements the **real shape** of every stage (genuine RRF, IDF sparse scoring, a relevance
gate, grounded generation) so the pipeline's control flow is exercised end-to-end without credentials.
Going live means implementing the same interfaces (`adapters/base.py`) against Sarvam / embeddinggemma
/ Qdrant / a hosted reranker / Gemma — **no caller changes**, per ADR-001. The Phase-3
`adapters/qdrant_real.py` already validates the collection contract (dense + native sparse, FK-only
payload) so later phases can rely on it.
