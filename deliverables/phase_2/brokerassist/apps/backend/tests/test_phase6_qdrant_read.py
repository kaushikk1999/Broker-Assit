"""Phase 6 real Qdrant READ adapter — filter builder + credential gating.

Live hybrid retrieval needs a real Qdrant (out of scope for credential-free CI). Here we verify the
metadata→Qdrant filter translation and that the factory stays on the mock until Qdrant is configured."""
import pytest

from app.adapters import get_vector_store
from app.adapters.mocks import MockVectorStore
from app.adapters.qdrant_real import build_qdrant_filter, QdrantReadStore


def test_factory_returns_mock_in_mocks_mode():
    assert isinstance(get_vector_store([]), MockVectorStore)


def test_read_store_requires_qdrant_url():
    # conftest sets BA_QDRANT_URL="" → construction must fail rather than silently no-op
    with pytest.raises(RuntimeError):
        QdrantReadStore()


def test_build_filter_none_when_empty():
    assert build_qdrant_filter(None) is None
    assert build_qdrant_filter({}) is None
    # source is not a payload field → dropped → no filter
    assert build_qdrant_filter({"source": ["NSE"]}) is None


def test_build_filter_scalar_company():
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    f = build_qdrant_filter({"company": "national aluminium"})
    assert isinstance(f, Filter) and len(f.must) == 1
    cond = f.must[0]
    assert isinstance(cond, FieldCondition) and cond.key == "company"
    assert isinstance(cond.match, MatchValue) and cond.match.value == "NALCO"


def test_build_filter_list_uses_match_any():
    from qdrant_client.models import MatchAny
    f = build_qdrant_filter({"filing_type": ["annual", "Board Meeting"]})
    cond = f.must[0]
    assert cond.key == "filing_type"
    assert isinstance(cond.match, MatchAny)
    # canonicalized: 'annual' → 'Annual Report'; 'Board Meeting' stays canonical
    assert set(cond.match.any) == {"Annual Report", "Board Meeting"}
