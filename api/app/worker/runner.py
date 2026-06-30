"""Phase 4 ingestion worker entrypoint (Railway `worker` service / local CLI).

Run once:
    python -m app.worker.runner --source nse --once
    python -m app.worker.runner --all --once
    python -m app.worker.runner --all --seed --once     # seed demo data first

Mocks-first by default: with BA_INGEST_LIVE=false (default) the run uses deterministic offline
fixtures — no credentials, no network. The scheduler/cadences (config) are wired in the deployed worker
only, never the web process, so the request path makes no live fetches."""
from __future__ import annotations

import argparse
import json

from app.db.base import SessionLocal
from app.ingestion.base import SOURCE_NAMES
from app.ingestion.orchestrator import ingest_all, ingest_source


def main() -> None:
    parser = argparse.ArgumentParser(description="BrokerAssist Phase 4 ingestion pipeline")
    parser.add_argument("--source", choices=SOURCE_NAMES, help="ingest a single source")
    parser.add_argument("--all", action="store_true", help="ingest every source once")
    parser.add_argument("--once", action="store_true", help="run a single pass and exit")
    parser.add_argument("--seed", action="store_true", help="seed demo data before running")
    args = parser.parse_args()

    if not args.source and not args.all:
        parser.error("specify --source <name> or --all")

    if args.seed:
        from app.db.seed import seed
        seed()

    db = SessionLocal()
    try:
        report = ingest_all(db) if args.all else ingest_source(db, args.source)
        print(json.dumps(report, indent=2, default=str))
    finally:
        db.close()


if __name__ == "__main__":
    main()
