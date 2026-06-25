"""Phase 5 config: canonical defaults + backward-compatible legacy env aliases."""
from app.config import Settings, settings


def test_phase5_defaults():
    assert settings.qdrant_collection_name == "brokerage_kb"
    assert settings.qdrant_dense_vector_name == "dense"
    assert settings.qdrant_sparse_vector_name == "sparse"
    assert settings.embedding_model == "embeddinggemma"
    assert settings.embedding_batch_size == 16
    assert settings.embedding_concurrency == 2
    assert settings.embedding_retry_count == 3
    assert settings.embedding_timeout_seconds == 30
    assert settings.ingestion_fail_fast is True
    assert settings.qdrant_create_collection_on_startup is False
    assert settings.language_codes == ["en", "hi", "ta"]
    assert "Board Meeting" in settings.filing_types and "FAQ" in settings.filing_types


def test_legacy_env_aliases(monkeypatch):
    monkeypatch.setenv("BA_QDRANT_COLLECTION", "legacy_kb")
    monkeypatch.setenv("BA_OLLAMA_API_KEY", "legacy-key")
    monkeypatch.setenv("BA_QDRANT_CREATE_IF_MISSING", "true")
    monkeypatch.setenv("BA_QDRANT_DENSE_DIM", "384")
    s = Settings()
    assert s.qdrant_collection_name == "legacy_kb"
    assert s.ollama_cloud_api_key == "legacy-key"
    assert s.qdrant_create_collection_on_startup is True
    assert s.embedding_dimension_override == 384


def test_canonical_env_takes_precedence(monkeypatch):
    monkeypatch.setenv("BA_QDRANT_COLLECTION_NAME", "brokerage_kb_v2")
    monkeypatch.setenv("BA_QDRANT_COLLECTION", "legacy_kb")
    monkeypatch.setenv("BA_OLLAMA_CLOUD_API_KEY", "canon-key")
    monkeypatch.setenv("BA_OLLAMA_API_KEY", "legacy-key")
    s = Settings()
    assert s.qdrant_collection_name == "brokerage_kb_v2"
    assert s.ollama_cloud_api_key == "canon-key"


def test_configured_helpers(monkeypatch):
    s = Settings()
    assert s.qdrant_configured is False and s.ollama_configured is False
    monkeypatch.setenv("BA_QDRANT_URL", "http://q:6333")
    monkeypatch.setenv("BA_OLLAMA_CLOUD_URL", "https://ollama")
    monkeypatch.setenv("BA_OLLAMA_CLOUD_API_KEY", "k")
    s2 = Settings()
    assert s2.qdrant_configured is True and s2.ollama_configured is True
