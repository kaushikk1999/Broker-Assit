"""Phase 5 embedding provider: mock dimension/probe/batch + real-adapter gating."""
import pytest

from app.adapters.mocks import MockEmbedding
from app.adapters import get_embedding


def test_mock_probe_dimension_default():
    e = MockEmbedding()
    assert e.probe_dimension() == 16
    assert len(e.embed("hello world")) == 16


def test_mock_configurable_dimension():
    e = MockEmbedding(dim=768)
    assert e.probe_dimension() == 768
    assert len(e.embed("x")) == 768


def test_mock_embed_batch_lengths():
    e = MockEmbedding(dim=8)
    vecs = e.embed_batch(["a", "b", "c"])
    assert len(vecs) == 3 and all(len(v) == 8 for v in vecs)
    assert e.embed_batch([]) == []


def test_mock_embed_deterministic():
    e = MockEmbedding()
    assert e.embed("same text") == e.embed("same text")
    assert e.embed("a") != e.embed("b")


def test_get_embedding_is_mock_in_mocks_mode():
    assert isinstance(get_embedding(), MockEmbedding)


def test_real_ollama_requires_config():
    from app.adapters.ollama_cloud import OllamaCloudEmbedding
    with pytest.raises(RuntimeError):
        OllamaCloudEmbedding(base_url="", api_key="")
