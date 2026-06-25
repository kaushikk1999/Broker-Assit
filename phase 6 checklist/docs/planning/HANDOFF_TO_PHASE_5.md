# 📌 HANDOFF — current status & how to structure Phase 5

> **Give this file to a fresh Claude session first.** It is the single entry point. It states the
> *true* current status, points to the detailed docs, and frames the next task: **structure Phase 5
> (Embedding Pipeline).** Last updated: **2026-06-24.**

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
| 3 — Backend Foundation | Auth, persistence, abuse control, module APIs, **Document Registry**, real-infra wiring | ✅ done & verified (20/20 tests) |
| **4 — Data Ingestion Layer** | 6 sources → parse → metadata → dedup → registry → chunk | 🟡 **analyzed & design-approved, NOT implemented** → [PHASE_4_PLAN.md](PHASE_4_PLAN.md) |
| **5 — Embedding Pipeline** | chunks → embed (embeddinggemma) + sparse → Qdrant `brokerage_kb` | ⛔ **to be structured next** → [PHASE_5_KICKOFF.md](PHASE_5_KICKOFF.md) |
| 6 — RAG System | hybrid retrieval + rerank + generate + cite | ⛔ later (consumer of Phase 5) |
| 7+ — Multilingual / NALCO pilot / launch | … | ⛔ later |

> ⚠️ **Phase 4 is planned, not built.** No ingestion code, worker, scheduler, or crawler exists yet
> (grep-confirmed). The plan in `PHASE_4_PLAN.md` is ready to implement; the three core design
> decisions are already locked. If you need Phase 4 *built* before Phase 5 can be verified end-to-end,
> say so — Phase 5 can still be **structured** now against the documented handoff contract.

## 3. Read order for the next agent

1. **This file** (orientation + status).
2. **[PHASE_STATUS.md](PHASE_STATUS.md)** — granular capability-level status (corrected numbering).
3. **[PHASE_4_PLAN.md](PHASE_4_PLAN.md)** — what Phase 4 will produce (Phase 5's *input*).
4. **[PHASE_5_KICKOFF.md](PHASE_5_KICKOFF.md)** — roadmap Phase 5 requirements, reuse/gaps, open
   questions, and the suggested method to structure Phase 5.
5. **[DECISIONS_AND_OPEN_ITEMS.md](DECISIONS_AND_OPEN_ITEMS.md)** — settled decisions (respect) vs open.
6. For *how the system works today:* `../overview/ARCHITECTURE.md`, `../reference/`.

## 4. Load-bearing invariants (never break)

1. Citations resolve from **PostgreSQL**, never Qdrant (payload = FKs + retrieval filters only).
2. Market data **never** comes from the vector store (separate cached branch).
3. **No model weights in-process** — every model is a remote call behind an adapter.
4. Security/abuse gate runs **before** any paid model call.
5. **Translate the query to English before retrieval.**
6. **Mocks-first must keep working** — full pipeline runs with `BA_USE_MOCKS=true`, zero credentials.
7. (Phase 5) Qdrant collection creation is a **startup** responsibility; **never hardcode** the
   embedding dimension — detect it dynamically.

## 5. The next task

**Structure Phase 5 — Embedding Pipeline** using [PHASE_5_KICKOFF.md](PHASE_5_KICKOFF.md): produce a
Phase-5 plan mirroring the Phase-4 plan's sections (goal, locked decisions, gap analysis, build order,
files, env vars, testing, rollback, and the Phase-5 → Phase-6 handoff), preserving all invariants and
the mocks-first path. **Stop at an approval gate before writing any code.**

## 6. Verify reality before trusting docs

```bash
cd deliverables/phase_2/brokerassist/apps/backend
python3.11 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
pytest -q                                   # expect: 20 passed
uvicorn app.main:app --port 8200            # /docs, /ready
```
