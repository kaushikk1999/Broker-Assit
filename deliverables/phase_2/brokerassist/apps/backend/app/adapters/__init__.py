"""Provider factory. Mocks-first; real vendors slot in when use_mocks=False (not yet implemented)."""
from app.config import settings
from app.adapters.mocks import (
    MockLanguage, MockEmbedding, MockReRanker, MockLLM, MockMarketData, MockVectorStore,
)


def get_language():
    if settings.use_mocks:
        return MockLanguage()
    raise NotImplementedError("Real Sarvam adapter not yet wired (provide BA_SARVAM_API_KEY).")


def get_embedding():
    if settings.use_mocks:
        return MockEmbedding()
    raise NotImplementedError("Real Ollama Cloud embeddinggemma adapter not yet wired.")


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
    """Mock store is built from the registry chunks. Real impl queries Qdrant by FK payload."""
    if settings.use_mocks:
        return MockVectorStore(chunks)
    raise NotImplementedError("Real Qdrant adapter not yet wired (provide BA_QDRANT_URL).")
