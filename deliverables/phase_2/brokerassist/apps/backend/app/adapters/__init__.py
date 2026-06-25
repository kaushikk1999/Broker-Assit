"""Provider factory. Mocks-first; real vendors slot in when configured (use_mocks=False + secrets)."""
from app.config import settings
from app.adapters.mocks import (
    MockLanguage, MockEmbedding, MockReRanker, MockLLM, MockMarketData,
    MockVectorStore, MockWritableVectorStore,
)


def get_language():
    if settings.use_mocks:
        return MockLanguage()
    raise NotImplementedError("Real Sarvam adapter not yet wired (provide BA_SARVAM_API_KEY).")


def get_embedding():
    """Phase 5: real embeddinggemma via Ollama Cloud when configured; mock otherwise (credential-free)."""
    if settings.use_mocks or not settings.ollama_configured:
        return MockEmbedding()
    from app.adapters.ollama_cloud import OllamaCloudEmbedding
    return OllamaCloudEmbedding()


def get_reranker():
    if settings.use_mocks:
        return MockReRanker()
    raise NotImplementedError("Real hosted re-ranker adapter not yet wired (provide BA_RERANKER_URL).")


def get_llm():
    if settings.use_mocks:
        return MockLLM()
    raise NotImplementedError("Real Ollama Cloud Gemma adapter not yet wired.")


def get_marketdata():
    if settings.use_mocks or settings.marketdata_provider == "mock":
        return MockMarketData()
    raise NotImplementedError("Real TrueData/Ticker adapter not yet wired.")


def get_vector_store(chunks):
    """Phase 6 READ side. Mock store is built from registry chunks; real impl queries Qdrant by FK."""
    if settings.use_mocks:
        return MockVectorStore(chunks)
    raise NotImplementedError("Real Qdrant read adapter not yet wired (Phase 6).")


# --- Phase 5 WRITE side (embedding pipeline) --------------------------------------------------------
_mock_writable: MockWritableVectorStore | None = None


def get_writable_vector_store():
    """Dual-vector WRITE store. Mock (in-memory singleton) unless a real Qdrant is configured."""
    global _mock_writable
    if settings.use_mocks or not settings.qdrant_configured:
        if _mock_writable is None:
            _mock_writable = MockWritableVectorStore()
        return _mock_writable
    from app.adapters.qdrant_real import QdrantWritableStore
    return QdrantWritableStore()


def reset_writable_vector_store() -> None:
    """Test helper: drop the in-memory mock store so each test starts clean."""
    global _mock_writable
    _mock_writable = None
