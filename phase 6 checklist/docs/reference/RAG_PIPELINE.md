# RAG Pipeline — deep dive

The knowledge branch (Branch B of the intent router) is the heart of BrokerAssist. This is the
stage-by-stage reference for `apps/backend/app/services/rag_pipeline.py` and the adapters it drives.

![RAG pipeline](../diagrams/rag-pipeline.svg)

*Raster copy: [`diagrams/rag-pipeline.png`](../diagrams/rag-pipeline.png)*

---

## When it runs

`POST /chat` first calls `intent_router.classify()`. If the message is **not** a market lookup
(market keyword **and** a known symbol), it enters this pipeline via `handle_knowledge(message,
user_lang, db, filters=None)`. The `/search` and `/filings` module endpoints reuse the same function
(`/filings` passes `filters={"source": ["NSE","BSE","NALCO_IR"]}`).

---

## The eight stages

| # | Stage | Code | Adapter (prod vendor) |
|---|---|---|---|
| 1 | Detect language | `language.detect()` (only if needed) | `LanguageProvider` (Sarvam) |
| 2 | Translate query → English | `language.translate(target="en")` | `LanguageProvider` (Sarvam) |
| 3 | Embed the English query | `embedding.embed()` | `EmbeddingProvider` (embeddinggemma) |
| 4 | Hybrid retrieve (dense + sparse, filtered) | `store.hybrid_search()` | `VectorStore` (Qdrant) |
| 5 | RRF fuse → Top-20 | inside `hybrid_search` | `VectorStore` |
| 6 | Cross-encoder rerank → Top-5 (+ relevance gate) | `reranker.rerank()` + `_is_relevant()` | `ReRanker` (bge) |
| 7 | Generate grounded answer | `llm.generate()` | `LLM` (Gemma) |
| 8 | Translate back + resolve citations | `language.translate()` + Postgres lookup | `LanguageProvider` + PostgreSQL |

### 1–2. Language detect & query translation
The query is **translated to English before retrieval** (`query_en = translate(message, "en", lang)`
when `user_lang != "en"`). This is the key move that makes Hindi/Tamil recall work against an
English-first index. In the mock (`adapters/mocks.py`), `MockLanguage.translate` maps HI/TA finance
terms (नालको→nalco, லாभांश/டிவிடெண்ட்→dividend, …) to English; Sarvam does this for real in production.

### 3. Embedding
`embedding.embed(query_en)` returns a dense vector. The mock returns a deterministic hash-based vector;
production uses Ollama Cloud · embeddinggemma. **No model weights run in-process** — it's a remote call
behind the adapter.

### 4–5. Hybrid retrieval + RRF
`store.hybrid_search(query_en, query_vec, top_k=BA_RETRIEVE_TOP_K, filters=...)` runs **two** retrievals
and fuses them with **Reciprocal Rank Fusion** (`rrf_score += 1/(k+rank)`, `k=60`):
- **Dense** — semantic similarity (mock proxy = token-overlap Jaccard).
- **Sparse** — keyword/lexical (mock = BM25-lite with IDF over the seeded chunks).
Filters are applied **at retrieval** (not post-hoc). Output: the fused **Top-20** candidate chunks.
Production swaps in Qdrant's native dense + sparse vectors; the FK-only payload means the fused result
carries `(document_id, chunk_id)` references, not citation text.

### 6. Rerank + relevance gate
`reranker.rerank(query_en, candidates, top_k=BA_RERANK_TOP_K)` re-scores the Top-20 with a
cross-encoder (mock = query/chunk token-overlap proxy) and keeps the **Top-5**.

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
