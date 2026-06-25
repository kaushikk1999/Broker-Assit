"""Phase 4 orchestrator — discover->parse->metadata->register->chunk, idempotency, and the no-vector
(hard stop before embedding) guarantee."""
from datetime import date

from app.adapters import get_writable_vector_store, reset_writable_vector_store
from app.db import models
from app.ingestion.base import RawDocument, SOURCE_NAMES, IngestionSource
from app.ingestion.orchestrator import ingest_all, ingest_source


def test_single_source_produces_documents_and_chunks(mem_db):
    report = ingest_source(mem_db, "nse")
    assert report["discovered"] == 2
    assert report["registered"] == 2
    assert report["chunks_written"] >= 2
    assert report["errors"] == []
    run = mem_db.query(models.IngestionRun).filter_by(source="nse").one()
    assert run.status == "success" and run.finished_at is not None


def test_ingest_all_covers_every_source(mem_db):
    report = ingest_all(mem_db)
    assert report["registered"] == mem_db.query(models.Document).count()
    assert report["chunks_written"] == mem_db.query(models.DocumentChunk).count()
    assert mem_db.query(models.IngestionRun).count() == len(SOURCE_NAMES)


def test_reingest_is_idempotent(mem_db):
    r1 = ingest_all(mem_db)
    docs_after_first = mem_db.query(models.Document).count()
    chunks_after_first = mem_db.query(models.DocumentChunk).count()
    r2 = ingest_all(mem_db)
    assert r2["registered"] == 0
    assert r2["duplicates"] == r1["registered"]
    assert r2["chunks_written"] == 0
    assert mem_db.query(models.Document).count() == docs_after_first
    assert mem_db.query(models.DocumentChunk).count() == chunks_after_first


def test_orchestrator_writes_no_vectors(mem_db):
    """The hard Phase 4/5 seam: ingestion must never touch the vector store."""
    reset_writable_vector_store()
    ingest_all(mem_db)
    assert get_writable_vector_store().count() == 0


def test_html_is_parsed_to_clean_text(mem_db):
    ingest_source(mem_db, "broker_site")
    chunk = mem_db.query(models.DocumentChunk).join(models.Document).filter(
        models.Document.source == "broker_site").first()
    assert chunk is not None
    assert "<" not in chunk.text and ">" not in chunk.text       # tags stripped
    assert "track(" not in chunk.text                            # <script> dropped


class _OneDocSource(IngestionSource):
    mode = "fixture"

    def __init__(self, name, body):
        self.name = name
        self._body = body

    def discover(self):
        return [RawDocument(source=self.name, url="https://x/changing", title="Changing doc",
                            content=self._body, content_type="text/plain",
                            filing_type="Quarterly Results", company="NALCO",
                            filing_date=date(2025, 5, 15))]


def test_changed_content_reversions_and_rewrites_chunks(mem_db):
    ingest_source(mem_db, "nse", source=_OneDocSource("nse", "original results body"))
    r2 = ingest_source(mem_db, "nse", source=_OneDocSource("nse", "revised results body with changes"))
    assert r2["versioned"] == 1
    doc = mem_db.query(models.Document).filter_by(url="https://x/changing").one()
    assert doc.document_version == 2
    # chunks were rewritten (delete-then-insert), not duplicated
    assert mem_db.query(models.DocumentChunk).filter_by(document_id=doc.id).count() >= 1
    assert "revised" in mem_db.query(models.DocumentChunk).filter_by(document_id=doc.id).first().text
