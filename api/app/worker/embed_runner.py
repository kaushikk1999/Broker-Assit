"""Phase 5 embedding worker entrypoint.

Run once (CLI / Railway `worker`):
    python -m app.worker.embed_runner --once
    python -m app.worker.embed_runner --seed --once     # seed demo data first

Mocks-first by default (credential-free). Set BA_USE_MOCKS=false + BA_HF_API_KEY + BA_QDRANT_* to
embed with the real Hugging Face model (bge-small) into a real Qdrant brokerage_kb collection."""
from __future__ import annotations

import argparse
import json

from app.db.base import SessionLocal
from app.services.embedding_pipeline import run_embedding_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="BrokerAssist Phase 5 embedding pipeline")
    parser.add_argument("--once", action="store_true", help="run a single pass and exit")
    parser.add_argument("--seed", action="store_true", help="seed demo data before running")
    args = parser.parse_args()

    if args.seed:
        from app.db.seed import seed
        seed()

    db = SessionLocal()
    try:
        report = run_embedding_pipeline(db)
        print(json.dumps(report, indent=2, default=str))
    finally:
        db.close()


if __name__ == "__main__":
    main()
