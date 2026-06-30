"""External-service interfaces. The roadmap mandates these be swappable (esp. MarketDataProvider).
No model weights run in-process: embeddings/LLM/rerank are remote calls behind these interfaces."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass


class CollectionContractError(RuntimeError):
    """Raised when the Qdrant collection's dense dim or vector schema does not match the embedding
    model. Phase 5 fails fast on this (when a real vector store is configured)."""


@dataclass
class RetrievedChunk:
    document_id: int
    chunk_id: int
    text: str
    score: float


# ---- Phase 5 (embedding pipeline) dual-vector primitives -----------------------------------------
@dataclass
class SparseVector:
    """Qdrant-native sparse vector: parallel index/value arrays (BM25/IDF applied by Qdrant)."""
    indices: list[int]
    values: list[float]


@dataclass
class VectorPoint:
    """One Qdrant point for the dual-vector brokerage_kb collection.

    payload holds ONLY foreign keys + retrieval filters (document_id, chunk_id, language, company,
    filing_type, date). Citation fields (source/url/version/checksum) are NEVER stored here."""
    point_id: int
    dense: list[float]
    sparse: SparseVector
    payload: dict


class LanguageProvider(ABC):
    """Sarvam AI in production."""
    @abstractmethod
    def detect(self, text: str) -> str: ...
    @abstractmethod
    def translate(self, text: str, target: str, source: str | None = None) -> str: ...


class EmbeddingProvider(ABC):
    """Ollama Cloud · embeddinggemma (multilingual). No local model weights run in-process."""
    @abstractmethod
    def embed(self, text: str, is_query: bool = False) -> list[float]: ...

    def embed_batch(self, texts: list[str], is_query: bool = False) -> list[list[float]]:
        """Default batch = sequential embed(); real adapters may override for true batching."""
        return [self.embed(t, is_query=is_query) for t in texts]

    def probe_dimension(self) -> int:
        """Detect the dense vector dimension dynamically (NEVER hardcode). Length of a probe embedding."""
        return len(self.embed("dimension probe"))


class VectorStore(ABC):
    """Qdrant (dense + native sparse) — READ side (Phase 6 retrieval). Payload holds only FKs."""
    @abstractmethod
    def hybrid_search(self, query: str, query_vector: list[float], top_k: int,
                      filters: dict | None = None) -> list[RetrievedChunk]: ...


class WritableVectorStore(ABC):
    """Qdrant dual-vector WRITE side (Phase 5 embedding pipeline). brokerage_kb collection lifecycle +
    idempotent dual-vector upsert. Collection creation is a startup responsibility, never per-document."""
    @abstractmethod
    def ensure_collection(self, dense_dim: int) -> dict:
        """Validate (and optionally create) the dual-vector collection for a probe-detected dense dim.
        Returns a status dict. Fails fast on dimension/schema mismatch when configured to."""
        ...

    @abstractmethod
    def upsert(self, points: list["VectorPoint"]) -> int:
        """Idempotent upsert keyed by point_id (= chunk_id). Returns number of points written."""
        ...

    @abstractmethod
    def delete(self, point_ids: list[int]) -> int:
        """Delete stale points (reindex). Returns number removed."""
        ...

    @abstractmethod
    def count(self) -> int:
        """Number of points currently stored."""
        ...


class ReRanker(ABC):
    """Hosted cross-encoder endpoint (e.g. BAAI/bge-reranker)."""
    @abstractmethod
    def rerank(self, query: str, chunks: list[RetrievedChunk], top_k: int) -> list[RetrievedChunk]: ...


class LLM(ABC):
    """Ollama Cloud · Gemma."""
    @abstractmethod
    def generate(self, query: str, context: list[str]) -> str: ...


class MarketDataProvider(ABC):
    """TrueData (primary) / Ticker / exchange feeds. Market data NEVER comes from Qdrant.

    The full roadmap interface (Source 2A) is LTP, OHLC, market depth, option chain and a tick
    subscription, so any provider — mock or a real REST/WebSocket vendor — is swappable behind it."""
    @abstractmethod
    def get_ltp(self, symbol: str) -> dict: ...
    @abstractmethod
    def get_ohlc(self, symbol: str) -> dict: ...
    @abstractmethod
    def get_market_depth(self, symbol: str) -> dict: ...
    @abstractmethod
    def get_option_chain(self, symbol: str) -> dict: ...
    @abstractmethod
    def subscribe_ticks(self, symbol: str, count: int = 1) -> list[dict]: ...
