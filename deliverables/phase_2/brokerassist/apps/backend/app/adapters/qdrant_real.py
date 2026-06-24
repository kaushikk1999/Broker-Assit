"""Qdrant connectivity + startup collection validation (Phase 3 scope ONLY).

No ingestion, no embeddings, no retrieval here. We assert the collection contract so later phases can
rely on it: dense + native sparse vectors, and a payload that holds ONLY foreign keys (document_id,
chunk_id). Citation fields must NEVER live in the Qdrant payload (they come from PostgreSQL)."""
from __future__ import annotations

from app.config import settings

# The ONLY payload fields Qdrant is allowed to store (foreign keys + retrieval filters added later).
PAYLOAD_CONTRACT = {"document_id", "chunk_id"}


def _client():
    from qdrant_client import QdrantClient  # lazy import (optional dep in dev)
    return QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None,
                        timeout=5.0)


def validate_collection() -> dict:
    """Returns a status dict; never raises (startup stays resilient). Statuses:
    skipped | ok | created | missing | dim_mismatch | no_sparse | unreachable."""
    name = settings.qdrant_collection
    if not settings.qdrant_url:
        return {"status": "skipped", "reason": "BA_QDRANT_URL not set", "collection": name}
    try:
        c = _client()
        exists = name in [col.name for col in c.get_collections().collections]
        if not exists:
            if settings.qdrant_create_if_missing:
                if not settings.qdrant_dense_dim:
                    return {"status": "missing", "collection": name,
                            "reason": "create_if_missing set but BA_QDRANT_DENSE_DIM not provided"}
                from qdrant_client.models import (
                    VectorParams, Distance, SparseVectorParams,
                )
                c.create_collection(
                    name,
                    vectors_config=VectorParams(size=settings.qdrant_dense_dim, distance=Distance.COSINE),
                    sparse_vectors_config={"text": SparseVectorParams()},
                )
                return {"status": "created", "collection": name, "dense_dim": settings.qdrant_dense_dim}
            return {"status": "missing", "collection": name,
                    "reason": "collection absent and create_if_missing=false"}

        info = c.get_collection(name)
        params = info.config.params
        # dense dim (handle single or named vector configs)
        dense_dim = None
        vectors = getattr(params, "vectors", None)
        if hasattr(vectors, "size"):
            dense_dim = vectors.size
        elif isinstance(vectors, dict) and vectors:
            first = next(iter(vectors.values()))
            dense_dim = getattr(first, "size", None)
        has_sparse = bool(getattr(params, "sparse_vectors", None))

        if settings.qdrant_dense_dim and dense_dim and dense_dim != settings.qdrant_dense_dim:
            return {"status": "dim_mismatch", "collection": name,
                    "expected": settings.qdrant_dense_dim, "actual": dense_dim}
        if not has_sparse:
            return {"status": "no_sparse", "collection": name, "dense_dim": dense_dim,
                    "reason": "native sparse vectors not configured (hybrid retrieval needs them)"}
        return {"status": "ok", "collection": name, "dense_dim": dense_dim,
                "has_sparse": True, "payload_contract": sorted(PAYLOAD_CONTRACT)}
    except Exception as e:
        return {"status": "unreachable", "collection": name, "error": type(e).__name__}


def qdrant_status() -> dict:
    """Lightweight reachability probe for /ready."""
    if not settings.qdrant_url:
        return {"configured": False}
    try:
        _client().get_collections()
        return {"configured": True, "reachable": True}
    except Exception as e:
        return {"configured": True, "reachable": False, "error": type(e).__name__}
