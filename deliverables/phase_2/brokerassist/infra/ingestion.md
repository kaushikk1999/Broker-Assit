# Data Ingestion (Phase 4) — runbook

Turns the five knowledge sources into clean, deduplicated, registered, **chunked** documents in
PostgreSQL — ready for Phase 5 to embed into Qdrant. It **stops before embeddings** (no vector writes).
Market data (Source 2A) is a separate cached, non-Qdrant branch and is never ingested here.

## Pipeline
```
source.discover() → parse (HTML/text) → metadata (canonical) → dedup/version (checksum)
                  → Document Registry (PostgreSQL) → chunk            [HARD STOP — no Qdrant]
```
Code lives in `app/ingestion/`; the worker entrypoint is `app/worker/runner.py`.

## Run it (mocks-first — no credentials, no network)
```bash
cd apps/backend && source .venv/bin/activate
python -m app.worker.runner --all --once          # ingest every source from offline fixtures
python -m app.worker.runner --source nse --once    # ingest a single source
python -m app.worker.runner --all --seed --once    # seed demo data first
```
Idempotent: re-running the same corpus produces identical checksums → all duplicates, no new chunks.
Changed content is re-versioned and its chunks are rewritten (never duplicated).

## Admin API (audited, admin-gated)
- `GET  /api/v1/admin/ingestion/sources` — sources, mode (fixture/live), cron cadence
- `GET  /api/v1/admin/ingestion/runs` — recent `IngestionRun` rows
- `POST /api/v1/admin/ingestion/run` — `{ "source": "nse" }` or `{ "all": true }`

## Going live (opt-in, needs credentials/deps)
Set `BA_INGEST_LIVE=true` and the per-source endpoints, then install optional parsers:
```bash
pip install -r requirements-ingest.txt
```
Live adapters live in `app/ingestion/sources/live_sources.py` (stubbed — they refuse to fetch until
wired). Endpoints / creds: `BA_BROKER_SITE_URL`, `BA_NSE_BASE_URL`, `BA_BSE_BASE_URL`,
`BA_NALCO_IR_URL`, `BA_GDRIVE_FOLDER_ID`, `BA_GDRIVE_CREDENTIALS_JSON`.

## Scheduling
Run-once now; recurring cadences (`BA_INGEST_CRON_{BROKER,NSE,BSE,NALCO,GDRIVE}`, defaults mirror the
roadmap refresh schedule) are wired in the Railway **worker** service only — never the web process, so
the request path makes no live fetches.
