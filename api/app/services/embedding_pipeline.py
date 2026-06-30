"""Phase 5 — Embedding Pipeline orchestration.

Reads registered chunks (PostgreSQL) -> validates metadata -> dense embed (Ollama Cloud · embeddinggemma)
+ native sparse (BM25/IDF) -> idempotent dual-vector upsert into Qdrant `brokerage_kb` with an FK-only
payload -> audit. Stops at the storage boundary: NO retrieval/RAG (that is Phase 6).

Idempotency: point_id = chunk_id, so re-running overwrites rather than duplicating. Reindex of a changed
chunk replaces its point. Citations are never written here — they resolve from PostgreSQL."""
from __future__ import annotations

import hashlib
import re

from sqlalchemy.orm import Session as DBSession

from app.config import settings
from app.adapters import get_embedding, get_writable_vector_store
from app.adapters.base import VectorPoint, SparseVector, CollectionContractError
from app.services.document_registry_service import chunks_with_documents, record_indexed
from app.services.metadata_contract import build_payload, MetadataValidationError

# Hashed-token space for the native sparse vector (Qdrant applies IDF over these term frequencies).
_SPARSE_DIM = 2 ** 20


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def sparse_encode(text: str) -> SparseVector:
    """Deterministic sparse vector: hashed token -> term frequency. Qdrant's IDF modifier weights it."""
    counts: dict[int, float] = {}
    for tok in _tokens(text):
        idx = int(hashlib.sha1(tok.encode()).hexdigest(), 16) % _SPARSE_DIM
        counts[idx] = counts.get(idx, 0.0) + 1.0
    indices = sorted(counts)
    return SparseVector(indices=indices, values=[counts[i] for i in indices])


def embedding_startup_check() -> dict:
    """Phase 5 startup readiness. CONDITIONAL fail-fast: validates the embedding/Qdrant contract only
    when a REAL vendor is configured; mocks mode (or unconfigured) always boots credential-free.

    Raises CollectionContractError to STOP startup when ingestion_fail_fast and a real, configured
    Qdrant/Ollama mismatches the contract (dim mismatch, missing sparse, missing collection w/ create
    disabled, or unreachable)."""
    if settings.use_mocks:
        return {"phase5": "mocks", "fatal": False}
    if not settings.qdrant_configured:
        return {"phase5": "qdrant_unconfigured", "fatal": False}

    from app.adapters.qdrant_real import validate_collection

    expected_dim = None
    if settings.embedding_provider != "mock" and (settings.ollama_configured or settings.hf_configured):
        try:
            expected_dim = get_embedding().probe_dimension()
        except Exception as e:
            if settings.ingestion_fail_fast:
                raise CollectionContractError(f"Embedding provider probe failed at startup: {e}")
            return {"phase5": "provider_unreachable", "error": str(e), "fatal": False}

    status = validate_collection(expected_dim=expected_dim)
    fatal = {"dim_mismatch", "no_sparse", "unreachable"}
    if not settings.qdrant_create_collection_on_startup:
        fatal = fatal | {"missing"}
    is_fatal = status.get("status") in fatal
    if is_fatal and settings.ingestion_fail_fast:
        raise CollectionContractError(f"Phase 5 startup validation failed: {status}")
    return {"phase5": status, "fatal": is_fatal}


def run_embedding_pipeline(db: DBSession, *, fail_fast: bool | None = None,
                           chunk_ids: list[int] | None = None) -> dict:
    """Embed registered chunks into the dual-vector collection. Returns a run report."""
    fail_fast = settings.ingestion_fail_fast if fail_fast is None else fail_fast
    embedder = get_embedding()
    store = get_writable_vector_store()

    # 1) Detect dense dimension dynamically (probe) — never hardcoded.
    dense_dim = embedder.probe_dimension()
    # 2) Validate (and optionally create) the collection for this dim — fails fast on mismatch.
    collection_status = store.ensure_collection(dense_dim)

    pairs = chunks_with_documents(db)
    if chunk_ids is not None:
        wanted = set(chunk_ids)
        pairs = [(c, d) for (c, d) in pairs if c.id in wanted]

    embedded = 0
    errors: list[dict] = []
    batch_size = max(1, settings.embedding_batch_size)

    for i in range(0, len(pairs), batch_size):
        prepared: list[tuple[object, dict]] = []
        for chunk, doc in pairs[i:i + batch_size]:
            try:
                payload = build_payload(
                    document_id=doc.id, chunk_id=chunk.id, language=chunk.lang,
                    company=doc.company, filing_type=doc.filing_type,
                    filing_date=doc.filing_date, strict=fail_fast,
                )
            except MetadataValidationError:
                if fail_fast:
                    raise
                errors.append({"chunk_id": chunk.id, "reason": "metadata_invalid"})
                continue
            prepared.append((chunk, payload))

        if not prepared:
            continue
        dense_vectors = embedder.embed_batch([c.text for c, _ in prepared])
        points = [
            VectorPoint(point_id=chunk.id, dense=dense, sparse=sparse_encode(chunk.text), payload=payload)
            for (chunk, payload), dense in zip(prepared, dense_vectors)
        ]
        embedded += store.upsert(points)

    # 3) Audit: mark each touched document as indexed.
    for doc_id in {d.id for _, d in pairs}:
        backend_name = "mock" if settings.use_mocks else settings.embedding_provider
        record_indexed(db, doc_id, {"backend": backend_name})

    return {
        "embedded": embedded,
        "dense_dim": dense_dim,
        "collection": collection_status.get("collection"),
        "collection_status": collection_status.get("status"),
        "total_points": store.count(),
        "errors": errors,
    }
