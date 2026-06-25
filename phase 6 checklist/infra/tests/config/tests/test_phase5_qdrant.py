"""Phase 5 vector store: dual-vector mock lifecycle, payload contract, fail-fast on mismatch."""
import pytest

from app.adapters.mocks import MockWritableVectorStore
from app.adapters.base import VectorPoint, SparseVector, CollectionContractError
from app.adapters.qdrant_real import PAYLOAD_CONTRACT, validate_collection


def _point(pid: int, dim: int = 16, payload: dict | None = None) -> VectorPoint:
    return VectorPoint(
        point_id=pid, dense=[0.1] * dim,
        sparse=SparseVector(indices=[1, 2], values=[1.0, 2.0]),
        payload=payload or {"document_id": pid, "chunk_id": pid, "language": "en",
                            "company": "NALCO", "filing_type": "FAQ", "date": "2025-01-01"},
    )


def test_payload_contract_is_six_keys():
    assert PAYLOAD_CONTRACT == {"document_id", "chunk_id", "language", "company", "filing_type", "date"}


def test_ensure_create_then_validate_ok():
    s = MockWritableVectorStore()
    assert s.ensure_collection(16)["status"] == "created"
    assert s.ensure_collection(16)["status"] == "ok"


def test_dimension_mismatch_fails_fast():
    s = MockWritableVectorStore()
    s.ensure_collection(16)
    with pytest.raises(CollectionContractError):
        s.ensure_collection(768)


def test_upsert_count_delete_idempotent():
    s = MockWritableVectorStore()
    s.ensure_collection(16)
    assert s.upsert([_point(1), _point(2)]) == 2
    assert s.count() == 2
    assert s.upsert([_point(1)]) == 1     # same point_id overwrites
    assert s.count() == 2                 # no duplicate
    assert s.delete([1]) == 1
    assert s.count() == 1


def test_upsert_rejects_wrong_dimension():
    s = MockWritableVectorStore()
    s.ensure_collection(16)
    with pytest.raises(CollectionContractError):
        s.upsert([_point(1, dim=8)])


def test_validate_collection_skips_without_url():
    # conftest sets BA_QDRANT_URL="" -> no network, status 'skipped'
    assert validate_collection()["status"] == "skipped"
