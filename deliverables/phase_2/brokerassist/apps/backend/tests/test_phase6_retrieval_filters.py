"""Phase 6 metadata filtering — applied AT retrieval (before fusion), mock = Qdrant parity.

The mock store is built from the canonical FK payloads, so a company filter narrows candidates exactly
like the real Qdrant adapter would, and unsupported keys (source) are dropped by normalize_filters."""
from app.db.base import SessionLocal
from app.db.seed import seed
from app.adapters import get_vector_store
from app.adapters.mocks import MockEmbedding
from app.services.rag_pipeline import _load_chunks
from app.services.metadata_contract import normalize_filters

seed()


def _store():
    db = SessionLocal()
    try:
        return get_vector_store(_load_chunks(db))
    finally:
        db.close()


def _vec():
    return MockEmbedding().embed("probe")


def test_company_filter_excludes_non_nalco_docs():
    store = _store()
    res = store.hybrid_search("white box black box algos", _vec(), top_k=20, filters={"company": "NALCO"})
    # the ALGO FAQ doc (company="") must be filtered out even though it best matches the query text
    assert res, "expected NALCO candidates"
    db = SessionLocal()
    try:
        from app.db import models
        for r in res:
            doc = db.get(models.Document, r.document_id)
            assert doc.company == "NALCO"
    finally:
        db.close()


def test_no_filter_returns_all():
    store = _store()
    res = store.hybrid_search("NALCO dividend results algo", _vec(), top_k=20, filters=None)
    assert len({r.document_id for r in res}) >= 4


def test_source_key_is_dropped_not_a_payload_field():
    # `source` is PostgreSQL-only → normalize_filters drops it (cannot filter Qdrant on it).
    assert normalize_filters({"source": ["NSE", "BSE"]}) == {}


def test_language_filter_off_by_default():
    # retrieval_language_filter defaults off → a language filter is a no-op
    assert normalize_filters({"language": "hi"}) == {}


def test_company_filter_is_canonicalized():
    assert normalize_filters({"company": "national aluminium"}) == {"company": "NALCO"}
