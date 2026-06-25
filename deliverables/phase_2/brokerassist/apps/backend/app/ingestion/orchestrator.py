"""Phase 4 ingestion orchestrator — discover -> parse -> metadata -> dedup/register -> chunk.

Hard seam (P4-D1): this stops at chunking. It writes ``Document`` / ``DocumentVersion`` /
``DocumentChunk`` / ``DocumentAuditHistory`` rows in PostgreSQL and **never** embeds or writes to Qdrant
— that is Phase 5. The orchestrator does not import any vector store or embedding provider, which is the
structural guarantee behind the "no vectors in Phase 4" invariant (a test asserts the vector store stays
empty after a run).

Idempotency: a re-run of the same fixture corpus produces identical checksums, so every document is a
duplicate and no new chunks are written. A changed document is re-versioned and its chunks are rewritten
(old chunks deleted first), never duplicated."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session as DBSession

from app.db import models
from app.ingestion import metadata as meta_extract
from app.ingestion import parsers
from app.ingestion.base import IngestionSource, SOURCE_NAMES, get_source
from app.ingestion.chunker import chunk_text
from app.ingestion.registry_service import register_document


def _rewrite_chunks(db: DBSession, document_id: int, text: str, lang: str) -> int:
    """Replace a document's chunks with a fresh chunking of its text (delete-then-insert)."""
    db.query(models.DocumentChunk).filter(
        models.DocumentChunk.document_id == document_id).delete()
    chunks = chunk_text(text)
    for i, body in enumerate(chunks):
        db.add(models.DocumentChunk(document_id=document_id, chunk_index=i, text=body, lang=lang))
    db.commit()
    return len(chunks)


def ingest_source(db: DBSession, name: str, *, source: IngestionSource | None = None,
                  actor: str = "worker") -> dict:
    """Run one source end-to-end (through chunking) and record an ``IngestionRun``. Returns a report."""
    source = source or get_source(name)
    run = models.IngestionRun(source=name, mode=source.mode, status="running")
    db.add(run); db.commit(); db.refresh(run)

    report = {"source": name, "mode": source.mode, "discovered": 0, "registered": 0,
              "versioned": 0, "duplicates": 0, "chunks_written": 0, "errors": [],
              "vectors_written": 0, "documents": []}
    try:
        raw_docs = source.discover()
        report["discovered"] = len(raw_docs)
        for raw in raw_docs:
            try:
                text = parsers.parse(raw.content, raw.content_type)
            except (parsers.UnsupportedContentType, parsers.ParserDependencyError, ValueError) as e:
                report["errors"].append({"url": raw.url, "reason": f"parse_failed: {e}"})
                continue
            if not text.strip():
                report["errors"].append({"url": raw.url, "reason": "empty_after_parse"})
                continue

            doc_meta = meta_extract.extract(raw, text)
            result = register_document(db, doc_meta, text, actor=actor)
            report[{"registered": "registered", "versioned": "versioned",
                    "duplicate": "duplicates"}[result.status]] += 1

            chunks = 0
            if result.should_chunk:
                chunks = _rewrite_chunks(db, result.document.id, text, doc_meta.lang)
                report["chunks_written"] += chunks
            report["documents"].append({"id": result.document.id, "status": result.status,
                                        "version": result.version, "chunks": chunks})

        run.status = "success"
    except Exception as e:  # noqa: BLE001 - record the failure on the run row, then re-raise
        run.status = "failed"
        report["errors"].append({"url": "", "reason": f"run_failed: {e}"})
        _finalize(db, run, report)
        raise
    _finalize(db, run, report)
    return report


def _finalize(db: DBSession, run: models.IngestionRun, report: dict) -> None:
    run.discovered = report["discovered"]
    run.registered = report["registered"]
    run.versioned = report["versioned"]
    run.duplicates = report["duplicates"]
    run.chunks_written = report["chunks_written"]
    run.errors = len(report["errors"])
    run.detail = {"errors": report["errors"], "documents": report["documents"]}
    run.finished_at = datetime.utcnow()
    db.commit()


def ingest_all(db: DBSession, *, actor: str = "worker") -> dict:
    """Run every ingestible source once and aggregate the per-source reports."""
    reports = [ingest_source(db, name, actor=actor) for name in SOURCE_NAMES]
    return {
        "sources": reports,
        "discovered": sum(r["discovered"] for r in reports),
        "registered": sum(r["registered"] for r in reports),
        "versioned": sum(r["versioned"] for r in reports),
        "duplicates": sum(r["duplicates"] for r in reports),
        "chunks_written": sum(r["chunks_written"] for r in reports),
        "errors": sum(len(r["errors"]) for r in reports),
    }
