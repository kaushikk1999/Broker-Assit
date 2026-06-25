# CLAUDE.md — project context for AI agents

**BrokerAssist** — a multi-tenant, embeddable, multilingual (EN/HI/TA), **cited** AI assistant for
stock brokerages. NALCO knowledge pilot, **mocks-first**.

## Start here
- **Phase 5 handoff (read first):** [docs/planning/HANDOFF_TO_PHASE_5.md](docs/planning/HANDOFF_TO_PHASE_5.md)
- **Agent guide:** [docs/CLAUDE.md](docs/CLAUDE.md) — orientation + where everything lives.
- **Current status:** [docs/planning/PHASE_STATUS.md](docs/planning/PHASE_STATUS.md)
- **Phase 4 plan (design-approved):** [docs/planning/PHASE_4_PLAN.md](docs/planning/PHASE_4_PLAN.md)
- **Phase 5 kickoff (structure next):** [docs/planning/PHASE_5_KICKOFF.md](docs/planning/PHASE_5_KICKOFF.md)
- **Full docs index:** [docs/README.md](docs/README.md)

## 30-second status
- Code lives in `deliverables/phase_2/brokerassist/` (FastAPI backend + Next.js frontend).
- **Phases 0–3 done & verified** (20/20 tests, full E2E). Runs **`BA_USE_MOCKS=true`** — zero credentials.
- **Phase numbering (roadmap):** 4 = Data Ingestion · 5 = Embedding · 6 = RAG · 7 = Multilingual. ("Real vendor adapters" is a cross-cutting wiring workstream, not a phase.)
- **Phase 4 — Data Ingestion Layer:** 🟡 analyzed & design-approved, **not implemented** (3 design decisions locked) → [PHASE_4_PLAN.md](docs/planning/PHASE_4_PLAN.md).
- **Not built yet:** Phase 4 ingestion code/worker, Phase 5 embedding pipeline, real vendor adapters, standalone widget, launch hardening.
- Next move: implement Phase 4 (fixtures-first, no creds), **or** structure Phase 5 → [PHASE_5_KICKOFF.md](docs/planning/PHASE_5_KICKOFF.md).

## Invariants — do NOT break
1. Citations resolve from **PostgreSQL**, never Qdrant (payload = FK only).
2. Market data **never** comes from the vector store (separate cached branch).
3. **No model weights in-process** — every model is a remote call behind an adapter.
4. The **security/abuse gate runs before any paid model call**.
5. **Translate the query to English before retrieval.**
6. **Mocks-first must keep working** — never make the default path depend on a live vendor.

## Run & verify
```bash
cd deliverables/phase_2/brokerassist/apps/backend && source .venv/bin/activate
pytest -q                                # expect: 20 passed
uvicorn app.main:app --port 8200         # /docs, /ready
```

## Working agreement
When you finish a unit of work, **update [docs/planning/PHASE_STATUS.md](docs/planning/PHASE_STATUS.md)**
and record any decision in
[docs/planning/DECISIONS_AND_OPEN_ITEMS.md](docs/planning/DECISIONS_AND_OPEN_ITEMS.md). Keep tests green
and the mocks-first path credential-free.
