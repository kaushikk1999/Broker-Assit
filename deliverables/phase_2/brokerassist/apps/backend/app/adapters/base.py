"""External-service interfaces. The roadmap mandates these be swappable (esp. MarketDataProvider).
No model weights run in-process: embeddings/LLM/rerank are remote calls behind these interfaces."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RetrievedChunk:
    document_id: int
    chunk_id: int
    text: str
    score: float


class LanguageProvider(ABC):
    """Sarvam AI in production."""
    @abstractmethod
    def detect(self, text: str) -> str: ...
    @abstractmethod
    def translate(self, text: str, target: str, source: str | None = None) -> str: ...


class EmbeddingProvider(ABC):
    """Ollama Cloud · embeddinggemma (multilingual)."""
    @abstractmethod
    def embed(self, text: str) -> list[float]: ...


class VectorStore(ABC):
    """Qdrant (dense + native sparse). Payload holds only FKs (document_id, chunk_id)."""
    @abstractmethod
    def hybrid_search(self, query: str, query_vector: list[float], top_k: int,
                      filters: dict | None = None) -> list[RetrievedChunk]: ...


class ReRanker(ABC):
    """Hosted cross-encoder endpoint (e.g. BAAI/bge-reranker)."""
    @abstractmethod
    def rerank(self, query: str, chunks: list[RetrievedChunk], top_k: int) -> list[RetrievedChunk]: ...


class LLM(ABC):
    """Ollama Cloud · Gemma."""
    @abstractmethod
    def generate(self, query: str, context: list[str]) -> str: ...


class MarketDataProvider(ABC):
    """TrueData (primary) / Ticker / exchange feeds. Market data NEVER comes from Qdrant."""
    @abstractmethod
    def get_ltp(self, symbol: str) -> dict: ...
    @abstractmethod
    def get_ohlc(self, symbol: str) -> dict: ...
