"""Phase 4 registry write-service — dedup, versioning, registration, audit (roadmap p. 10 rules)."""
from datetime import date

from app.db import models
from app.ingestion.metadata import DocumentMeta
from app.ingestion.registry_service import compute_checksum, register_document


def _meta(url="https://x/doc1", title="Doc 1", ftype="Quarterly Results", company="NALCO"):
    return DocumentMeta(source="nse", url=url, title=title, company=company,
                        filing_type=ftype, filing_date=date(2025, 5, 15), lang="en")


def test_checksum_is_deterministic_64_hex():
    a = compute_checksum("hello world")
    assert a == compute_checksum("hello world")
    assert len(a) == 64 and all(c in "0123456789abcdef" for c in a)
    assert a != compute_checksum("HELLO WORLD")


def test_new_document_is_registered_with_version_1(mem_db):
    res = register_document(mem_db, _meta(), "first body of text")
    assert res.status == "registered" and res.version == 1 and res.should_chunk
    assert mem_db.query(models.Document).count() == 1
    assert mem_db.query(models.DocumentVersion).filter_by(version=1).count() == 1
    assert mem_db.query(models.DocumentAuditHistory).filter_by(action="registered").count() == 1


def test_identical_text_is_a_duplicate_no_new_version(mem_db):
    register_document(mem_db, _meta(), "same body")
    res = register_document(mem_db, _meta(), "same body")
    assert res.status == "duplicate" and res.should_chunk is False
    assert mem_db.query(models.Document).count() == 1
    assert mem_db.query(models.DocumentVersion).count() == 1  # no new version row
    assert mem_db.query(models.DocumentAuditHistory).filter_by(action="duplicate").count() == 1


def test_changed_text_same_url_creates_new_version(mem_db):
    register_document(mem_db, _meta(), "original body")
    res = register_document(mem_db, _meta(title="Doc 1 (rev)"), "revised body with new numbers")
    assert res.status == "versioned" and res.version == 2 and res.should_chunk
    assert mem_db.query(models.Document).count() == 1            # same logical doc, updated in place
    doc = mem_db.query(models.Document).first()
    assert doc.document_version == 2
    assert mem_db.query(models.DocumentVersion).count() == 2     # v1 + v2
    assert mem_db.query(models.DocumentAuditHistory).filter_by(action="updated").count() == 1


def test_distinct_urls_are_distinct_documents(mem_db):
    register_document(mem_db, _meta(url="https://x/a"), "body a")
    register_document(mem_db, _meta(url="https://x/b"), "body b")
    assert mem_db.query(models.Document).count() == 2
