"""Phase 5 pipeline: end-to-end mock embed -> sparse -> dual-vector upsert, idempotency, citations."""
from app.db.base import SessionLocal
from app.db.seed import seed
from app.adapters import reset_writable_vector_store, get_writable_vector_store
from app.services.embedding_pipeline import (
    run_embedding_pipeline, sparse_encode, embedding_startup_check,
)
from app.services.document_registry_service import resolve_citation

seed()  # ensure the 4-doc NALCO knowledge base + chunks exist


def test_pipeline_embeds_all_seed_chunks():
    reset_writable_vector_store()
    db = SessionLocal()
    try:
        report = run_embedding_pipeline(db)
        assert report["embedded"] >= 4
        assert report["dense_dim"] == 16
        assert report["collection"] == "brokerage_kb"
        assert report["collection_status"] in {"created", "ok"}
        assert report["total_points"] == report["embedded"]
        assert report["errors"] == []
    finally:
        db.close()


def test_pipeline_is_idempotent():
    reset_writable_vector_store()
    db = SessionLocal()
    try:
        r1 = run_embedding_pipeline(db)
        r2 = run_embedding_pipeline(db)   # same in-memory store -> overwrite, not duplicate
        assert r2["total_points"] == r1["total_points"]
    finally:
        db.close()


def test_payload_is_fk_only_and_citations_from_postgres():
    reset_writable_vector_store()
    db = SessionLocal()
    try:
        run_embedding_pipeline(db)
        store = get_writable_vector_store()
        allowed = {"document_id", "chunk_id", "language", "company", "filing_type", "date"}
        for point in store._points.values():
            assert set(point.payload) == allowed
            for forbidden in ("url", "source", "checksum", "document_version", "title"):
                assert forbidden not in point.payload
        # citation fields resolve from PostgreSQL, not the Qdrant payload
        cit = resolve_citation(db, document_id=1, chunk_id=1)
        assert cit and cit["url"] and cit["source"]
    finally:
        db.close()


def test_reindex_replaces_without_duplicates():
    reset_writable_vector_store()
    db = SessionLocal()
    try:
        run_embedding_pipeline(db)
        store = get_writable_vector_store()
        before = store.count()
        run_embedding_pipeline(db)
        assert store.count() == before
    finally:
        db.close()


def test_sparse_encode_deterministic_nonempty():
    a = sparse_encode("NALCO quarterly results dividend")
    b = sparse_encode("NALCO quarterly results dividend")
    assert a.indices == b.indices and a.values == b.values
    assert len(a.indices) == len(a.values) > 0


def test_startup_check_mocks_is_non_fatal():
    st = embedding_startup_check()
    assert st["fatal"] is False
    assert st["phase5"] == "mocks"
