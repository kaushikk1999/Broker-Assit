"""Document Registry write-service (Phase 4) — dedup, versioning, registration, audit.

Implements the roadmap "Duplicate Detection Rules" (p. 10): compute checksum -> search the documents
table -> if the checksum already exists, skip (duplicate); if the same logical document exists with a
*different* checksum, create a new version; otherwise register a new document. Citation fields live
here in PostgreSQL — never in Qdrant.

This is the WRITE complement to ``app.services.document_registry_service`` (which is read-side lookups
used by Phases 5/6). Chunk writing is owned by the orchestrator; this service owns Document /
DocumentVersion / DocumentAuditHistory rows."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

from sqlalchemy.orm import Session as DBSession

from app.db import models
from app.ingestion.metadata import DocumentMeta


def compute_checksum(text: str) -> str:
    """Stable SHA-256 over the cleaned document text (full 64-hex; fits Document.checksum)."""
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


@dataclass
class RegisterResult:
    document: models.Document
    status: str          # "registered" | "versioned" | "duplicate"
    version: int
    checksum: str
    should_chunk: bool   # True when content is new/changed and the caller should (re)write chunks


def _find_existing(db: DBSession, meta: DocumentMeta) -> models.Document | None:
    """Locate the same logical document: by (source, url) when a url is known, else (source, title)."""
    q = db.query(models.Document).filter(models.Document.source == meta.source)
    if meta.url:
        return q.filter(models.Document.url == meta.url).first()
    return q.filter(models.Document.title == meta.title).first()


def register_document(db: DBSession, meta: DocumentMeta, text: str, *,
                      actor: str = "ingestion") -> RegisterResult:
    """Dedup/version/register a discovered document. Commits and returns the outcome."""
    checksum = compute_checksum(text)

    # Rule 3 — exact duplicate anywhere in the registry: skip (no new version, no re-chunk).
    dup = db.query(models.Document).filter(models.Document.checksum == checksum).first()
    if dup is not None:
        db.add(models.DocumentAuditHistory(
            document_id=dup.id, action="duplicate", actor=actor,
            detail={"checksum": checksum, "source": meta.source}))
        db.commit()
        return RegisterResult(dup, "duplicate", dup.document_version, checksum, should_chunk=False)

    existing = _find_existing(db, meta)
    if existing is not None:
        # Rule 4 — same document, changed content: create a new version and refresh the registry row.
        new_version = existing.document_version + 1
        existing.title = meta.title
        existing.filing_type = meta.filing_type
        existing.filing_date = meta.filing_date
        existing.company = meta.company
        existing.checksum = checksum
        existing.document_version = new_version
        existing.updated_at = _now()
        db.add(models.DocumentVersion(document_id=existing.id, version=new_version,
                                      checksum=checksum, change_note="content changed"))
        db.add(models.DocumentAuditHistory(document_id=existing.id, action="updated", actor=actor,
                                           detail={"version": new_version, "checksum": checksum}))
        db.commit()
        return RegisterResult(existing, "versioned", new_version, checksum, should_chunk=True)

    # New document.
    doc = models.Document(
        source=meta.source, url=meta.url, company=meta.company, filing_type=meta.filing_type,
        filing_date=meta.filing_date, title=meta.title, document_version=1, checksum=checksum)
    db.add(doc)
    db.flush()
    db.add(models.DocumentVersion(document_id=doc.id, version=1, checksum=checksum,
                                  change_note="initial"))
    db.add(models.DocumentAuditHistory(document_id=doc.id, action="registered", actor=actor,
                                       detail={"source": meta.source, "title": meta.title}))
    db.commit()
    return RegisterResult(doc, "registered", 1, checksum, should_chunk=True)


def _now():
    from datetime import datetime
    return datetime.utcnow()
