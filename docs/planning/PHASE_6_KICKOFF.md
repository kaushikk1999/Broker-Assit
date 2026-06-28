# Phase 6 — RAG System (kickoff brief for structuring)

> **Purpose of this file:** give the next agent everything needed to **structure Phase 6 (RAG System)** the same way Phase 5 was structured — roadmap requirements extracted, current-code reuse/gaps mapped, the handoff contract stated, invariants restated, and the open questions surfaced.
> **This is a planning scaffold, not an implementation.**
>
> **Source of truth:** roadmap pp. 20–22 (Phase 6 — RAG System).

---

## 1. Phase 6 goal (roadmap)

Wire up the real retrieval-augmented generation (RAG) pipeline behind swappable provider interfaces: **Sarvam AI** for multilingual translation, **Ollama Cloud** (Gemma) for grounded LLM generation, **Qdrant** (`brokerage_kb`) for hybrid (dense+sparse) retrieval with metadata filters, and a **hosted cross-encoder reranker** for precision filtering. The system must run end-to-end against real endpoints when credentials are provided, while fully preserving the credential-free mocks-first mode.

## 2. Roadmap requirements (extracted, pp. 20–22)

**Multilingual query handling**
- Language detection and query-to-English translation using **Sarvam AI** (for Hindi/Tamil queries).
- Retrieval must always happen in English against the English-first index for maximum recall.
- Response must be translated back to the user's original language using Sarvam.

**Hybrid retrieval & RRF**
- Query Qdrant `brokerage_kb` using the dense query vector (`embeddinggemma`) and a sparse query vector (`BM25/IDF`).
- Apply metadata filters (language, company, filing_type, date) **at retrieval time** directly in Qdrant (not post-hoc).
- Merge dense and sparse retrieval scores using **Reciprocal Rank Fusion (RRF)** to extract the Top-20 candidates.

**Cross-encoder reranking**
- Send the Top-20 chunks to a hosted cross-encoder reranker model (such as `bge-reranker-large`).
- Rerank results and extract the Top-5 chunks for the generation context window.

**Relevance gate**
- Ensure query is relevant to the retrieved chunks before citing or generating.
- If the reranked chunks do not meet the minimum relevance threshold (or have zero token overlap), abort and return a friendly localized fallback response with **no citations** (prevents citing off-topic filings).

**Grounded generation**
- Generate the final answer using Gemma (served by Ollama Cloud), grounded **strictly** in the context of the Top-5 retrieved chunks.
- The prompt must instruct the model to only use the provided context and refuse to hallucinate.

**Citation resolution**
- Resolve citation details (`source`, `url`, `title`, `filing_date`) from **PostgreSQL** using the chunk/document foreign keys.
- Do not store citation text in Qdrant.

---

## 3. Current code — reuse vs gaps for Phase 6

| Asset | Where | State for Phase 6 |
|---|---|---|
| RAG Pipeline Orchestrator | `app/services/rag_pipeline.py` | ✅ reuse. `handle_knowledge` implements the exact 8-stage sequence. Needs verification that it correctly drives real adapters when `BA_USE_MOCKS=false`. |
| Qdrant read adapter | `app/adapters/qdrant_real.py` | 🔧 **implement**. Needs a `QdrantReadStore` implementing the `VectorStore` interface (specifically `hybrid_search` with RRF and metadata filters). |
| Ollama Cloud LLM | `app/adapters/ollama_cloud.py` | 🔧 **implement**. Needs `OllamaCloudLLM` implementing the `LLM` interface to make API calls to Gemma on Ollama Cloud. |
| Sarvam translation | `app/adapters/sarvam.py` | 🔧 **new**. Create a `SarvamLanguageProvider` implementing `LanguageProvider` to handle detection and translation. |
| Reranker adapter | `app/adapters/reranker_real.py` | 🔧 **new**. Create a `HostedReRanker` implementing `ReRanker` to call the cross-encoder endpoint. |
| Adapter factories | `app/adapters/__init__.py` | 🔧 **wire**. Update `get_language`, `get_reranker`, `get_llm`, and `get_vector_store` to instantiate real adapters when `settings.use_mocks` is `False`. |

---

## 4. Phase-5 → Phase-6 handoff contract

**Input to Phase 6** (established by Phase 5):
- The `brokerage_kb` collection exists in Qdrant with dense + sparse vector settings.
- The `get_writable_vector_store()` factory returns a store capable of writing dense/sparse points and dynamic dimension probe detection.
- Mocks-first indexing behaves identically to the planned Qdrant indexing shape.

**Phase 6 task**:
- Implement the read-side of Qdrant (hybrid dense/sparse retrieval with metadata filters and RRF).
- Wire up the external model APIs (Sarvam, Ollama LLM, reranker).
- Verify the end-to-end retrieval and answer loop against both mocks and real endpoints.

---

## 5. Invariants Phase 6 must preserve

1. **Citations resolve from PostgreSQL, never Qdrant** (payload = FKs + retrieval filters only). *(ADR-002)*
2. **Market data never comes from the vector store** (intent routing forks market queries to cache). *(ADR-004)*
3. **No model weights in-process** — all translation, embedding, reranking, and generation run behind adapter APIs. *(ADR-001)*
4. **Security/abuse gate runs before paid model calls** (rate limits, tenant quotas, lockout checks). *(ADR-005)*
5. **Translate queries to English before retrieval** to achieve multilingual recall.
6. **Mocks-first must keep working** — the whole pipeline must execute credential-free when `BA_USE_MOCKS=true`.

---

## 6. Open questions to resolve when structuring Phase 6

1. **RRF logic placement**: Should RRF be computed client-side in the backend adapter (`qdrant_real.py`) after retrieving dense and sparse lists separately, or does the Qdrant deployment support a query API that handles fusion server-side? (Recommend: Client-side fusion in `QdrantReadStore` for maximum environment compatibility).
2. **Reranker hosting**: Where is the reranker hosted? Does it run on Ollama Cloud or a dedicated endpoint? (ADR-007 target).
3. **Relevance gate threshold**: What metric/threshold determines if the retrieved context is "relevant" in production? In mocks, it uses a token overlap check; in production, cross-encoder scores can define a numerical threshold.
4. **Timeout & fallback policies**: If Sarvam or Ollama Cloud is slow or down, does the RAG pipeline fail fast, time out, or use a cached/mock fallback? (Recommend: fail fast with clean user-facing error messages, logged carefully).

---

## 7. How to structure Phase 6 (suggested method for the next agent)

1. Produce an implementation plan in `implementation_plan.md` with:
   - Specific file modifications needed in `app/adapters/` and `app/services/`.
   - Environment variables needed for Sarvam, Reranker, and Qdrant read.
   - Verification plan using both unit tests (`pytest`) and manual curl tests.
2. Ensure mock tests (like `test_pipeline.py`) continue to pass.
3. Write credential-gated integration tests (e.g. `test_phase6_real.py`) that run against real API endpoints when keys are present in the environment, and skip gracefully when absent.
4. Obtain approval on the implementation plan before writing code.
