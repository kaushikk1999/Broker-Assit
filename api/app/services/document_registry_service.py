"""Document Registry lookups — the single source of truth for citations (PostgreSQL).

Phase 5 writes ONLY foreign keys + filters into Qdrant; every citation field (source, url, version,
checksum) is resolved here from PostgreSQL. This service also supplies the chunk->document join the
embedding pipeline needs to assemble payload metadata."""
from __future__ import annotations

from sqlalchemy.orm import Session as DBSession

from app.db import models


def get_document(db: DBSession, document_id: int) -> models.Document | None:
    return db.get(models.Document, document_id)


def get_chunk(db: DBSession, chunk_id: int) -> models.DocumentChunk | None:
    return db.get(models.DocumentChunk, chunk_id)


def chunks_with_documents(db: DBSession) -> list[tuple[models.DocumentChunk, models.Document]]:
    """All chunks joined to their parent document (skips orphans). Phase 5's embedding input."""
    pairs: list[tuple[models.DocumentChunk, models.Document]] = []
    for ch in db.query(models.DocumentChunk).order_by(models.DocumentChunk.id).all():
        doc = db.get(models.Document, ch.document_id)
        if doc is not None:
            pairs.append((ch, doc))
    return pairs


def resolve_citation(db: DBSession, document_id: int, chunk_id: int | None = None) -> dict | None:
    """Resolve full citation metadata from PostgreSQL (NEVER from the Qdrant payload)."""
    doc = db.get(models.Document, document_id)
    if doc is None:
        return None
    return {
        "document_id": doc.id,
        "chunk_id": chunk_id,
        "source": doc.source,
        "url": doc.url,
        "title": doc.title,
        "document_version": doc.document_version,
        "checksum": doc.checksum,
        "filing_date": doc.filing_date.isoformat() if doc.filing_date else None,
    }


def record_indexed(db: DBSession, document_id: int, detail: dict | None = None) -> None:
    """Write an audit row marking a document's chunks as indexed into Qdrant."""
    db.add(models.DocumentAuditHistory(
        document_id=document_id, action="reindexed", actor="embedding_pipeline",
        detail=detail or {}))
    db.commit()
