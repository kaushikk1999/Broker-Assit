"""Phase 6 hosted cross-encoder re-ranker — scoring, response shapes, fallback, and gating."""
import pytest

from app.adapters import get_reranker
from app.adapters.mocks import MockReRanker
from app.adapters.base import RetrievedChunk
from app.adapters.reranker_cloud import HostedReRanker, _parse_scores


def _chunks():
    return [
        RetrievedChunk(document_id=1, chunk_id=1, text="alpha doc", score=0.9),
        RetrievedChunk(document_id=2, chunk_id=2, text="beta doc", score=0.8),
        RetrievedChunk(document_id=3, chunk_id=3, text="gamma doc", score=0.7),
    ]


def test_factory_is_mock_in_mocks_mode():
    assert isinstance(get_reranker(), MockReRanker)


def test_requires_url():
    with pytest.raises(RuntimeError):
        HostedReRanker(url="")


def test_parse_scores_shapes():
    assert _parse_scores({"scores": [0.1, 0.2, 0.3]}, 3) == [0.1, 0.2, 0.3]
    assert _parse_scores([0.1, 0.2], 2) == [0.1, 0.2]
    # out-of-order index objects are placed back into input order
    got = _parse_scores({"results": [{"index": 2, "score": 0.9},
                                     {"index": 0, "score": 0.1},
                                     {"index": 1, "score": 0.5}]}, 3)
    assert got == [0.1, 0.5, 0.9]
    assert _parse_scores({"data": [{"index": 0, "relevance_score": 0.4},
                                   {"index": 1, "relevance_score": 0.6}]}, 2) == [0.4, 0.6]


def test_parse_scores_length_mismatch_raises():
    with pytest.raises(RuntimeError):
        _parse_scores({"scores": [0.1]}, 3)


def test_rerank_sorts_by_score(monkeypatch):
    rr = HostedReRanker(url="https://rerank.example/score")
    # gamma(0.99) > alpha(0.5) > beta(0.1)
    monkeypatch.setattr(rr, "_score", lambda q, docs: [0.5, 0.1, 0.99])
    out = rr.rerank("q", _chunks(), top_k=2)
    assert [c.document_id for c in out] == [3, 1]
    assert out[0].score == pytest.approx(0.99)


def test_rerank_falls_back_to_rrf_order_on_failure(monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "rerank_fallback_enabled", True)
    rr = HostedReRanker(url="https://rerank.example/score")

    def boom(q, docs):
        raise RuntimeError("endpoint down")

    monkeypatch.setattr(rr, "_score", boom)
    out = rr.rerank("q", _chunks(), top_k=2)
    # incoming order preserved (already RRF-sorted), no exception
    assert [c.document_id for c in out] == [1, 2]


def test_rerank_raises_when_fallback_disabled(monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "rerank_fallback_enabled", False)
    rr = HostedReRanker(url="https://rerank.example/score")
    monkeypatch.setattr(rr, "_score", lambda q, docs: (_ for _ in ()).throw(RuntimeError("down")))
    with pytest.raises(RuntimeError):
        rr.rerank("q", _chunks(), top_k=2)
