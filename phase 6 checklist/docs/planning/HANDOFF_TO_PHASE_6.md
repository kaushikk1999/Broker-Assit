# 📌 HANDOFF — current status & how to structure Phase 6

> **Give this file to a fresh Claude session first.** It is the single entry point. It states the
> *true* current status, points to the detailed docs, and frames the next task: **structure Phase 6
> (RAG System).** Last updated: **2026-06-25.**

---

## 1. What this project is

**BrokerAssist** — a multi-tenant, embeddable, multilingual (EN/HI/TA), **cited** AI assistant for
stock brokerages. NALCO knowledge pilot. **Mocks-first** (runs credential-free).
Code: `deliverables/phase_2/brokerassist/` (FastAPI backend + Next.js frontend).

## 2. True current status (read this carefully)

| Phase (roadmap numbering) | Scope | Status |
|---|---|---|
| 0 — Research | Competitive/gap analysis | ✅ done |
| 1 — UX Design | IA, journeys, wireframes, widget | ✅ done |
| 2 — System Architecture + thin slice | Mocks-first NALCO RAG slice + widget security | ✅ done & verified |
| 3 — Backend Foundation | Auth, persistence, abuse control, module APIs, **Document Registry**, real-infra wiring | ✅ done & verified |
| **4 — Data Ingestion Layer** | 6 sources → parse → metadata → dedup → registry → chunk | 🟡 **analyzed & design-approved, NOT implemented** → [PHASE_4_PLAN.md](file:///Users/kaushikkarmakar/Downloads/AI%20bot/docs/planning/PHASE_4_PLAN.md) |
| **5 — Embedding Pipeline** | chunks → embed (embeddinggemma) + sparse → Qdrant `brokerage_kb` | ✅ **Implemented mocks-first** (51/51 tests green) → [PHASE_5_KICKOFF.md](file:///Users/kaushikkarmakar/Downloads/AI%20bot/docs/planning/PHASE_5_KICKOFF.md) |
| **6 — RAG System** | hybrid retrieval + rerank + generate + cite | ⛔ **to be structured next** → [PHASE_6_KICKOFF.md](file:///Users/kaushikkarmakar/Downloads/AI%20bot/docs/planning/PHASE_6_KICKOFF.md) |
| 7 — Multilingual Layer | real Sarvam EN/HI/TA detect/translate | 🟡 mock exists; real = Sarvam adapter |
| 8+ — NALCO pilot / launch | … | ⛔ later |

> ⚠️ **Phase 4 is planned, not built.** However, Phase 5 has been successfully implemented mocks-first (using mock vectors, mock write storage, and a runner) with 31 new tests, meaning we have a solid, working foundation for document representation.
> Phase 6 can now be **structured** and built mocks-first, consuming the mock vector database outputs or Postgres registry entries.

## 3. Read order for the next agent

1. **This file** (orientation + status).
2. **[PHASE_STATUS.md](file:///Users/kaushikkarmakar/Downloads/AI%20bot/docs/planning/PHASE_STATUS.md)** — granular capability-level status (corrected numbering, now updated to 51 tests).
3. **[PHASE_6_KICKOFF.md](file:///Users/kaushikkarmakar/Downloads/AI%20bot/docs/planning/PHASE_6_KICKOFF.md)** — roadmap Phase 6 requirements, reuse/gaps, open decisions, and the suggested method to structure Phase 6.
4. **[PHASE_5_KICKOFF.md](file:///Users/kaushikkarmakar/Downloads/AI%20bot/docs/planning/PHASE_5_KICKOFF.md)** — what Phase 5 produced (Phase 6's index layer).
5. **[PHASE_4_PLAN.md](file:///Users/kaushikkarmakar/Downloads/AI%20bot/docs/planning/PHASE_4_PLAN.md)** — details of the ingestion layer.
6. **[DECISIONS_AND_OPEN_ITEMS.md](file:///Users/kaushikkarmakar/Downloads/AI%20bot/docs/planning/DECISIONS_AND_OPEN_ITEMS.md)** — settled decisions (respect) vs open.
7. For *how the system works today:* `../overview/ARCHITECTURE.md`, `../reference/`.

## 4. Load-bearing invariants (never break)

1. Citations resolve from **PostgreSQL**, never Qdrant (payload = FKs + retrieval filters only). *(ADR-002)*
2. Market data **never** comes from the vector store (separate cached branch). *(ADR-004)*
3. **No model weights in-process** — every model is a remote call behind an adapter. *(ADR-001)*
4. Security/abuse gate runs **before** any paid model call. *(ADR-005)*
5. **Translate the query to English before retrieval** (multilingual recall).
6. **Mocks-first must keep working** — full pipeline runs with `BA_USE_MOCKS=true`, zero credentials.
7. Qdrant collection creation is a **startup** responsibility; **never hardcode** the embedding dimension — detect it dynamically (implemented in Phase 5).

## 5. The next task

**Structure Phase 6 — RAG System** using [PHASE_6_KICKOFF.md](file:///Users/kaushikkarmakar/Downloads/AI%20bot/docs/planning/PHASE_6_KICKOFF.md): produce a Phase-6 implementation plan (goal, open questions, proposed changes, files, verification plan), preserving all invariants and the mocks-first path. **Stop at an approval gate before writing any code.**

## 6. Verify reality before trusting docs

```bash
cd deliverables/phase_2/brokerassist/apps/backend
source .venv/bin/activate
pytest -q                                   # expect: 51 passed
uvicorn app.main:app --port 8200            # then hit /ready, /docs
```
