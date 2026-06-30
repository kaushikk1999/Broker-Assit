"""Qdrant integration — connectivity, dual-vector collection lifecycle, and Phase 5 upsert.

Collection `brokerage_kb` holds a NAMED dense vector (size = probe-detected dim, COSINE) and a Qdrant
NATIVE sparse vector (BM25/IDF). The payload stores ONLY foreign keys + retrieval filters; citation
fields come from PostgreSQL and must NEVER be written here.

Design:
- Dense dimension is detected dynamically (probe) and passed in — NEVER hardcoded.
- Collection creation is a STARTUP responsibility (ensure_collection), never per-document.
- validate_collection() is non-raising (status dict) so /ready stays resilient; ensure_collection()
  fails fast (CollectionContractError) on dim/schema mismatch for the ingestion path."""
from __future__ import annotations

from app.config import settings
from app.adapters.base import (
    WritableVectorStore, VectorStore, VectorPoint, RetrievedChunk, CollectionContractError,
)

# The ONLY payload fields Qdrant may store: foreign keys (document_id, chunk_id) + retrieval filters.
PAYLOAD_CONTRACT = {"document_id", "chunk_id", "language", "company", "filing_type", "date"}


def _client():
    from qdrant_client import QdrantClient  # lazy import (optional dep in dev)
    return QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None, timeout=10.0)


def _inspect_dense_sparse(params) -> tuple[int | None, bool]:
    """Extract (dense_dim, has_named_sparse) from a collection's params (named or single vector)."""
    dense_dim = None
    vectors = getattr(params, "vectors", None)
    if isinstance(vectors, dict) and vectors:
        entry = vectors.get(settings.qdrant_dense_vector_name) or next(iter(vectors.values()))
        dense_dim = getattr(entry, "size", None)
    elif hasattr(vectors, "size"):
        dense_dim = vectors.size
    sparse = getattr(params, "sparse_vectors", None)
    has_sparse = bool(sparse) and (
        settings.qdrant_sparse_vector_name in sparse if isinstance(sparse, dict) else True)
    return dense_dim, has_sparse


def validate_collection(expected_dim: int | None = None) -> dict:
    """Non-raising status probe used at startup/readiness. Statuses:
    skipped | ok | created | missing | dim_mismatch | no_sparse | unreachable."""
    name = settings.qdrant_collection_name
    want_dim = expected_dim if expected_dim is not None else settings.embedding_dimension_override
    if not settings.qdrant_url:
        return {"status": "skipped", "reason": "BA_QDRANT_URL not set", "collection": name}
    try:
        c = _client()
        exists = name in [col.name for col in c.get_collections().collections]
        if not exists:
            return {"status": "missing", "collection": name,
                    "reason": "collection absent (create via ensure_collection)"}
        info = c.get_collection(name)
        dense_dim, has_sparse = _inspect_dense_sparse(info.config.params)
        if want_dim and dense_dim and dense_dim != want_dim:
            return {"status": "dim_mismatch", "collection": name,
                    "expected": want_dim, "actual": dense_dim}
        if not has_sparse:
            return {"status": "no_sparse", "collection": name, "dense_dim": dense_dim,
                    "reason": "native sparse vector not configured (hybrid retrieval needs it)"}
        return {"status": "ok", "collection": name, "dense_dim": dense_dim, "has_sparse": True,
                "payload_contract": sorted(PAYLOAD_CONTRACT)}
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


def build_qdrant_filter(filters: dict | None):
    """Translate a normalized retrieval-filter dict into a Qdrant `Filter` (must-match conditions).

    Returns None when there is nothing to filter on. List values become MatchAny (match any of);
    scalars become MatchValue. The dict is first canonicalized by the metadata contract so the mock and
    Qdrant filter identically; only payload filter fields survive (document_id/chunk_id are FKs)."""
    from app.services.metadata_contract import normalize_filters
    from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny

    nfilters = normalize_filters(filters)
    if not nfilters:
        return None
    must = []
    for key, want in nfilters.items():
        if isinstance(want, list):
            must.append(FieldCondition(key=key, match=MatchAny(any=want)))
        else:
            must.append(FieldCondition(key=key, match=MatchValue(value=want)))
    return Filter(must=must)


class QdrantReadStore(VectorStore):
    """Phase 6 READ side — hybrid dense + native sparse retrieval over `brokerage_kb`, fused with
    server-side Reciprocal Rank Fusion, with metadata filters applied AT retrieval on BOTH branches.

    The Qdrant payload holds ONLY foreign keys + filters, so candidates come back with FKs + score and
    NO text; chunk text and citations are hydrated from PostgreSQL downstream (citation invariant)."""

    def __init__(self):
        if not settings.qdrant_url:
            raise RuntimeError("Qdrant read store not configured (set BA_QDRANT_URL).")
        self.name = settings.qdrant_collection_name
        self.dense = settings.qdrant_dense_vector_name
        self.sparse = settings.qdrant_sparse_vector_name
        self._client = _client()

    def hybrid_search(self, query: str, query_vector, top_k, filters=None) -> list[RetrievedChunk]:
        from qdrant_client.models import Prefetch, FusionQuery, Fusion, SparseVector as QSparse
        from app.services.embedding_pipeline import sparse_encode

        sv = sparse_encode(query)  # SAME encoder used at ingestion → sparse query/index parity
        qfilter = build_qdrant_filter(filters)
        prefetch = [
            Prefetch(query=list(query_vector), using=self.dense, filter=qfilter, limit=top_k),
            Prefetch(query=QSparse(indices=sv.indices, values=sv.values), using=self.sparse,
                     filter=qfilter, limit=top_k),
        ]
        resp = self._client.query_points(
            collection_name=self.name, prefetch=prefetch,
            query=FusionQuery(fusion=Fusion.RRF), limit=top_k, with_payload=True,
        )
        out: list[RetrievedChunk] = []
        for p in resp.points:
            payload = p.payload or {}
            doc_id = payload.get("document_id")
            chunk_id = payload.get("chunk_id", p.id)
            if doc_id is None:
                continue  # malformed point without the FK — skip rather than cite blindly
            out.append(RetrievedChunk(document_id=int(doc_id), chunk_id=int(chunk_id),
                                      text="", score=float(p.score)))
        return out


class QdrantWritableStore(WritableVectorStore):
    """Real dual-vector store for brokerage_kb (Phase 5). Fails fast on dim/schema mismatch."""

    def __init__(self):
        self.name = settings.qdrant_collection_name
        self.dense = settings.qdrant_dense_vector_name
        self.sparse = settings.qdrant_sparse_vector_name
        self._client = _client()

    def ensure_collection(self, dense_dim: int) -> dict:
        from qdrant_client.models import (
            VectorParams, Distance, SparseVectorParams, Modifier,
        )
        exists = self.name in [c.name for c in self._client.get_collections().collections]
        if not exists:
            if not settings.qdrant_create_collection_on_startup:
                raise CollectionContractError(
                    f"collection {self.name!r} missing and creation disabled "
                    f"(set BA_QDRANT_CREATE_COLLECTION_ON_STARTUP=true to create)")
            self._client.create_collection(
                self.name,
                vectors_config={self.dense: VectorParams(size=dense_dim, distance=Distance.COSINE)},
                sparse_vectors_config={self.sparse: SparseVectorParams(modifier=Modifier.IDF)},
            )
            return {"status": "created", "collection": self.name, "dense_dim": dense_dim}
        info = self._client.get_collection(self.name)
        actual_dim, has_sparse = _inspect_dense_sparse(info.config.params)
        if actual_dim and actual_dim != dense_dim:
            raise CollectionContractError(
                f"dense dim mismatch for {self.name}: collection={actual_dim} model={dense_dim}")
        if not has_sparse:
            raise CollectionContractError(
                f"collection {self.name} has no native sparse vector {self.sparse!r}")
        return {"status": "ok", "collection": self.name, "dense_dim": actual_dim}

    def upsert(self, points: list[VectorPoint]) -> int:
        from qdrant_client.models import PointStruct, SparseVector as QSparse
        structs = []
        for p in points:
            disallowed = set(p.payload) - PAYLOAD_CONTRACT
            if disallowed:
                raise CollectionContractError(f"payload has disallowed keys: {sorted(disallowed)}")
            structs.append(PointStruct(
                id=p.point_id,
                vector={self.dense: p.dense,
                        self.sparse: QSparse(indices=p.sparse.indices, values=p.sparse.values)},
                payload=p.payload,
            ))
        self._client.upsert(collection_name=self.name, points=structs)
        return len(structs)

    def delete(self, point_ids: list[int]) -> int:
        if not point_ids:
            return 0
        self._client.delete(collection_name=self.name, points_selector=list(point_ids))
        return len(point_ids)

    def count(self) -> int:
        return self._client.count(collection_name=self.name).count
