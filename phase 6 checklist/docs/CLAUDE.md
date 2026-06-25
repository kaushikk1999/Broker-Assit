# Agent Guide — start here if you're continuing this project

You are picking up **BrokerAssist**: a multi-tenant, embeddable, multilingual (EN/HI/TA), **cited** AI
assistant for stock brokerages. This file orients you in ~2 minutes and points you to the exact docs
for status and planning.

## 1. Orient (read in this order)

1. **[planning/PHASE_STATUS.md](planning/PHASE_STATUS.md)** — the current state of every phase &
   capability (✅/🟡/⛔/⚠️). **Always read this first; treat it as the source of truth.**
2. **[planning/NEXT_PHASE_PLAN.md](planning/NEXT_PHASE_PLAN.md)** — what to build next, with file-level
   steps, gates, and acceptance criteria.
3. **[planning/DECISIONS_AND_OPEN_ITEMS.md](planning/DECISIONS_AND_OPEN_ITEMS.md)** — what's settled
   (respect it) vs what's open (may block you).
4. **[planning/ROADMAP.md](planning/ROADMAP.md)** — the visual phase map.

For *how the system works*, see [overview/ARCHITECTURE.md](overview/ARCHITECTURE.md) and the
[reference/](reference/) docs.

## 2. The 30-second status

- **Code:** `deliverables/phase_2/brokerassist/` (FastAPI backend + Next.js frontend monorepo).
- **Phases 0–3 are DONE and verified** (20/20 tests, full E2E). The pilot runs **mocks-first**
  (`BA_USE_MOCKS=true`) with **zero credentials**.
- **What's NOT built:** real vendor adapters, the ingestion/embedding worker, the standalone widget
  package, production hardening.
- **Best next move with no credentials:** scaffold the **ingestion worker**
  ([plan §A](planning/NEXT_PHASE_PLAN.md#workstream-a--ingestion--embedding-worker--no-credentials-needed-to-scaffold)).
- **Best next move with a vendor key:** wire that **real adapter**
  ([plan §C](planning/NEXT_PHASE_PLAN.md#workstream-c--real-vendor-adapters-phase-4---needs-credentials-one-vendor-at-a-time)).

## 3. Invariants — do NOT break these

1. Citations resolve from **PostgreSQL**, never Qdrant (Qdrant payload = FK only). *(ADR-002)*
2. Market data **never** comes from the vector store — separate cached branch. *(ADR-004)*
3. **No model weights run in-process** — every model is a remote call behind an adapter. *(ADR-001)*
4. The **security/abuse gate runs before any paid model call**. *(ADR-005)*
5. **Translate the query to English before retrieval** (multilingual recall).
6. **Mocks-first must keep working** — the full pipeline runs credential-free; never add a hard
   dependency on a live vendor in the default path.

## 4. How to run & verify (confirm reality before trusting docs)

```bash
cd deliverables/phase_2/brokerassist/apps/backend
python3.11 -m venv .venv && source .venv/bin/activate   # if not already
pip install -r requirements.txt
pytest -q                                                # expect: 20 passed
uvicorn app.main:app --port 8200                         # /docs, /ready
```
Frontend: `cd ../frontend && npm install && npm run dev` (port 3000).
Full guide: [reference/SETUP_AND_RUN.md](reference/SETUP_AND_RUN.md). Test details:
[reference/TESTING.md](reference/TESTING.md).

## 5. Where things live (backend `app/`)

| Need to change… | Go to |
|---|---|
| A vendor integration | `adapters/base.py` (interface) + `adapters/__init__.py` (factory) + a new `adapters/<vendor>.py` |
| The RAG flow | `services/rag_pipeline.py` |
| Routing market vs knowledge | `services/intent_router.py` |
| Auth / sessions | `core/security.py` (widget) · `core/admin_security.py` (admin) |
| Rate limits / quotas | `core/ratelimit.py` |
| DB schema | `db/models.py` (+ a new Alembic revision) |
| Endpoints | `api/routes_*.py` |
| Config / env vars | `config.py` (all `BA_`-prefixed) |

## 6. When you finish a unit of work

1. Add/extend tests; keep `pytest -q` green and mocks-first running credential-free.
2. Update the changed rows in **[planning/PHASE_STATUS.md](planning/PHASE_STATUS.md)** (⛔/⚠️ → ✅).
3. If you made an architectural decision, record it in
   **[planning/DECISIONS_AND_OPEN_ITEMS.md](planning/DECISIONS_AND_OPEN_ITEMS.md)** (new D# / close an
   open ADR) and the
   [readiness scorecard](../deliverables/phase_2/discovery/03_readiness_scorecard.md).
4. Re-verify links if you moved docs (`docs/` uses relative links).

> Keeping these planning docs current is what lets the *next* agent start fast. Treat updating them as
> part of the task, not an afterthought.
