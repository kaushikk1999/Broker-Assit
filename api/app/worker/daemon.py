"""Phase 4/5 background worker daemon.

Runs continuously in the Railway `worker` service. Uses APScheduler to trigger
the ingestion and embedding pipelines according to the configured cron cadences.
"""
from __future__ import annotations

import logging
import signal
import sys
import threading
from typing import Any

from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.observability import configure_logging, log
from app.db.base import SessionLocal
from app.ingestion.scheduler import cadences, Cadence
from app.ingestion.orchestrator import ingest_source
from app.services.embedding_pipeline import run_embedding_pipeline

# Prevent overlapping jobs per source
_job_locks: dict[str, threading.Lock] = {}


def _run_ingest_and_embed(source_name: str) -> None:
    """Run ingestion for a single source, followed by the embedding pipeline."""
    lock = _job_locks.setdefault(source_name, threading.Lock())
    if not lock.acquire(blocking=False):
        log.warning("Skipping scheduled run for '%s': previous run still active.", source_name)
        return

    try:
        log.info("Starting scheduled ingestion for source: %s", source_name)
        db = SessionLocal()
        try:
            report = ingest_source(db, source_name, actor="scheduler")
            log.info("Ingestion report for '%s': discovered=%d registered=%d versioned=%d duplicates=%d chunks=%d",
                     source_name, report["discovered"], report["registered"], report["versioned"],
                     report["duplicates"], report["chunks_written"])
            
            # If new chunks were written, trigger embedding pipeline to vectorise them
            if report["chunks_written"] > 0:
                log.info("New chunks written, triggering embedding pipeline...")
                embed_report = run_embedding_pipeline(db)
                log.info("Embedding report: %s", embed_report)
        finally:
            db.close()
    except Exception as e:
        log.error("Scheduled job for '%s' failed: %s", source_name, e, exc_info=True)
    finally:
        lock.release()


def main() -> None:
    configure_logging()
    log.info("Starting BrokerAssist background daemon...")

    scheduler = BlockingScheduler()

    # Wire up the cadences from configuration
    configured_cadences = cadences()
    jobs_added = 0
    for cad in configured_cadences:
        if not cad.cron or cad.cron == "":
            log.warning("Skipping source '%s': no cron cadence configured.", cad.source)
            continue
        
        # fields: minute hour dom month dow
        m, h, d, mon, dow = cad.fields
        trigger = CronTrigger(minute=m, hour=h, day=d, month=mon, day_of_week=dow)
        
        scheduler.add_job(
            _run_ingest_and_embed,
            trigger=trigger,
            args=[cad.source],
            id=f"job_{cad.source}",
            name=f"Ingest {cad.source}",
            max_instances=1
        )
        jobs_added += 1
        log.info("Scheduled '%s' with cron: %s", cad.source, cad.cron)

    if jobs_added == 0:
        log.error("No valid cadences found. Daemon will exit.")
        sys.exit(1)

    def shutdown(signum: int, frame: Any) -> None:
        log.info("Shutting down daemon...")
        scheduler.shutdown(wait=True)
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    scheduler.start()


if __name__ == "__main__":
    main()
