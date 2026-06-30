"""Provider factory. Mocks-first; real vendors slot in when configured (use_mocks=False + secrets)."""
from app.config import settings
from app.adapters.mocks import (
    MockLanguage, MockEmbedding, MockReRanker, MockLLM, MockMarketData,
    MockVectorStore, MockWritableVectorStore,
)


def get_language():
    """Phase 6: real Sarvam detect/translate when configured (BA_SARVAM_API_KEY); mock otherwise."""
    if settings.use_mocks or not settings.sarvam_configured:
        return MockLanguage()
    from app.adapters.sarvam_cloud import SarvamLanguage
    return SarvamLanguage()


def get_embedding():
    """Phase 5: real embeddinggemma via Ollama Cloud when configured; mock otherwise (credential-free).

    `BA_EMBEDDING_PROVIDER` overrides the default: "mock" forces the deterministic mock even when
    use_mocks is off (Ollama Cloud has no embedding models, so dense embeddings have no live provider);
    "ollama" forces the real adapter; "auto" (default) uses the real adapter only when configured."""
    if settings.embedding_provider == "mock":
        return MockEmbedding()
    if settings.embedding_provider == "hf" or (settings.embedding_provider == "auto" and not settings.use_mocks and settings.hf_configured):
        from app.adapters.hf_cloud import HuggingFaceEmbedding
        return HuggingFaceEmbedding()
    if settings.embedding_provider == "ollama" or (settings.embedding_provider == "auto" and not settings.use_mocks and settings.ollama_configured):
        from app.adapters.ollama_cloud import OllamaCloudEmbedding
        return OllamaCloudEmbedding()
    return MockEmbedding()


def get_reranker():
    """Phase 6: hosted cross-encoder when configured (BA_RERANKER_URL); mock otherwise (credential-free)."""
    if settings.use_mocks or not settings.reranker_configured:
        return MockReRanker()
    from app.adapters.reranker_cloud import HostedReRanker
    return HostedReRanker()


def get_llm():
    """Phase 6: real Gemma generation (Ollama Cloud) when configured; mock otherwise (credential-free)."""
    if settings.use_mocks or not settings.generation_configured:
        return MockLLM()
    from app.adapters.ollama_cloud import OllamaCloudLLM
    return OllamaCloudLLM()


def get_marketdata():
    if settings.use_mocks or settings.marketdata_provider == "mock":
        return MockMarketData()
    raise NotImplementedError("Real TrueData/Ticker adapter not yet wired.")


def get_vector_store(chunks):
    """Phase 6 READ side. Mock store is built from registry chunks; the real impl queries Qdrant by FK
    (hybrid dense+sparse → server-side RRF, filters at retrieval) and ignores `chunks`."""
    if settings.use_mocks or not settings.qdrant_configured:
        return MockVectorStore(chunks)
    from app.adapters.qdrant_real import QdrantReadStore
    return QdrantReadStore()


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
