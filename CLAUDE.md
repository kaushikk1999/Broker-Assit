# CLAUDE.md — project context for AI agents

**BrokerAssist** — a multi-tenant, embeddable, multilingual (EN/HI/TA), **cited** AI assistant for
stock brokerages. NALCO knowledge pilot, **mocks-first**.

## Start here
- **Current status (read first):** [docs/planning/PHASE_STATUS.md](docs/planning/PHASE_STATUS.md) — source of truth for what's built.
- **Agent guide:** [docs/CLAUDE.md](docs/CLAUDE.md) — orientation + where everything lives.
- **Phase 4 plan (now implemented):** [docs/planning/PHASE_4_PLAN.md](docs/planning/PHASE_4_PLAN.md)
- **What to build next:** [docs/planning/NEXT_PHASE_PLAN.md](docs/planning/NEXT_PHASE_PLAN.md)
- **Full docs index:** [docs/README.md](docs/README.md)

## 30-second status
- Code lives in `deliverables/phase_2/brokerassist/` (FastAPI backend + Next.js frontend).
- **Phases 0–6 implemented, mocks-first** (142/142 tests, full E2E). Runs **`BA_USE_MOCKS=true`** — zero credentials.
- **Phase numbering (roadmap):** 4 = Data Ingestion · 5 = Embedding · 6 = RAG · 7 = Multilingual. ("Real vendor adapters" is a cross-cutting wiring workstream, not a phase.)
- **Phase 4 — Data Ingestion Layer:** ✅ implemented fixtures-first (`app/ingestion/` + `app/worker/runner.py`; sources→parse→metadata→dedup→registry→chunk, hard stop before embeddings). Live crawl/NSE/BSE/Drive gated on `BA_INGEST_LIVE` → [PHASE_4_PLAN.md](docs/planning/PHASE_4_PLAN.md).
- **Phase 7 — Multilingual:** 🟡 partial (Sarvam detect/translate built; transliteration/STT/TTS/UI to do).
- **Not built yet:** live source crawls + real vendor adapters (credential-gated), standalone widget, launch hardening.
- Next move: finish Phase 7 multilingual extras (mostly mocks-first), **or** wire a live source / real vendor (needs creds).

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
pytest -q                                # expect: 142 passed
python -m app.worker.runner --all --seed --once # Phase 4 ingestion (--seed bootstraps schema+demo data on a fresh DB; offline fixtures → registry → chunks)
uvicorn app.main:app --port 8200         # /docs, /ready
```

## Working agreement
When you finish a unit of work, **update [docs/planning/PHASE_STATUS.md](docs/planning/PHASE_STATUS.md)**
and record any decision in
[docs/planning/DECISIONS_AND_OPEN_ITEMS.md](docs/planning/DECISIONS_AND_OPEN_ITEMS.md). Keep tests green
and the mocks-first path credential-free.
