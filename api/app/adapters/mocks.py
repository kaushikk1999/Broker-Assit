"""Deterministic mock providers (mocks-first). Each implements a base interface so the real vendor
(Sarvam / Ollama Cloud / Qdrant / hosted re-ranker / TrueData) can drop in without touching callers."""
from __future__ import annotations
import hashlib
import math
import re

from app.config import settings
from app.adapters.base import (
    LanguageProvider, EmbeddingProvider, VectorStore, WritableVectorStore, ReRanker, LLM,
    MarketDataProvider, RetrievedChunk, VectorPoint, CollectionContractError,
)

_DEVANAGARI = re.compile(r"[ऀ-ॿ]")
_TAMIL = re.compile(r"[஀-௿]")

# Query-side normalization so HI/TA queries retrieve against an English index (roadmap Phase 6/7).
_TO_EN = {
    "नालको": "nalco", "नैल्को": "nalco", "நால்கோ": "nalco",
    "परिणाम": "result", "முடிவு": "result", "முடிவை": "result",
    "तिमाही": "quarterly", "காலாண்டு": "quarterly",
    "लाभांश": "dividend", "டிவிடெண்ட்": "dividend",
    "एल्गो": "algo", "அல்கோ": "algo",
    "शेयर": "share", "பங்கு": "stock", "कीमत": "price", "விலை": "price",
}
# Response-side canned translations for the seeded NALCO answer (reuse prototype dictionary).
_ANSWER_TRANSLATIONS = {
    "hi": "NALCO ने इस तिमाही अधिक राजस्व दर्ज किया, जो बेहतर एल्युमिना कीमतों से प्रेरित था। "
          "पिछली तिमाही की तुलना में शुद्ध लाभ बढ़ा।",
    "ta": "NALCO இந்த காலாண்டில் அதிக வருவாயைப் பதிவு செய்தது, வலுவான அலுமினா விலைகளால் "
          "இயக்கப்பட்டது. முந்தைய காலாண்டை விட நிகர லாபம் உயர்ந்தது.",
}


def _stem(tok: str) -> str:
    """Tiny suffix stripper so 'quarterly'~'quarter' and 'results'~'result' match (mock only)."""
    for suf in ("ations", "ation", "ing", "ies", "ly", "ed", "es", "s"):
        if len(tok) > len(suf) + 2 and tok.endswith(suf):
            return tok[: -len(suf)]
    return tok


def _tokens(text: str) -> list[str]:
    return [_stem(t) for t in re.findall(r"[a-z0-9]+", text.lower())]


class MockLanguage(LanguageProvider):
    def detect(self, text: str) -> str:
        if _TAMIL.search(text):
            return "ta"
        if _DEVANAGARI.search(text):
            return "hi"
        return "en"

    def translate(self, text: str, target: str, source: str | None = None) -> str:
        if target == "en":
            out = text
            for k, v in _TO_EN.items():
                out = out.replace(k, v)
            return out
        # Response translation: use canned NALCO answer if the English answer matches the seed.
        if target in _ANSWER_TRANSLATIONS and "NALCO" in text and "revenue" in text.lower():
            return _ANSWER_TRANSLATIONS[target]
        return text  # mock: unknown phrases pass through


class MockEmbedding(EmbeddingProvider):
    """Deterministic stand-in for embeddinggemma. Dimension is configurable so Phase 5 can exercise
    dynamic dimension detection without a live model (default 16)."""
    def __init__(self, dim: int = 16):
        self._dim = dim

    def embed(self, text: str, is_query: bool = False) -> list[float]:
        # Deterministic vector of length self._dim by hashing (text + block index).
        out: list[float] = []
        block = 0
        while len(out) < self._dim:
            h = hashlib.sha256(f"{text}#{block}".encode()).digest()
            out.extend(b / 255.0 for b in h)
            block += 1
        return out[: self._dim]


class MockWritableVectorStore(WritableVectorStore):
    """In-memory dual-vector store standing in for Qdrant brokerage_kb (Phase 5). Persists points so a
    test can upsert then read back. Enforces the dense-dimension contract and fails fast on mismatch."""
    def __init__(self):
        self._points: dict[int, VectorPoint] = {}
        self._dense_dim: int | None = None

    def ensure_collection(self, dense_dim: int) -> dict:
        name = settings.qdrant_collection_name
        if self._dense_dim is None:
            self._dense_dim = dense_dim
            return {"status": "created", "collection": name, "dense_dim": dense_dim,
                    "vectors": [settings.qdrant_dense_vector_name, settings.qdrant_sparse_vector_name]}
        if self._dense_dim != dense_dim:
            raise CollectionContractError(
                f"dense dim mismatch for {name}: collection={self._dense_dim} model={dense_dim}")
        return {"status": "ok", "collection": name, "dense_dim": dense_dim}

    def upsert(self, points: list[VectorPoint]) -> int:
        for p in points:
            if self._dense_dim is not None and len(p.dense) != self._dense_dim:
                raise CollectionContractError(
                    f"point {p.point_id} dense len {len(p.dense)} != collection dim {self._dense_dim}")
            self._points[p.point_id] = p  # idempotent: keyed by point_id (= chunk_id)
        return len(points)

    def delete(self, point_ids: list[int]) -> int:
        removed = 0
        for pid in point_ids:
            if pid in self._points:
                del self._points[pid]
                removed += 1
        return removed

    def count(self) -> int:
        return len(self._points)


class MockVectorStore(VectorStore):
    """Dense (semantic proxy = token overlap) + sparse (BM25-lite IDF) → RRF, filtered at retrieval.

    Accepts chunks as (document_id, chunk_id, text) or (document_id, chunk_id, text, payload). When a
    payload (the canonical FK + filter dict from `metadata_contract.build_payload`) is supplied, metadata
    filters are applied AT retrieval on both branches — mirroring the real Qdrant adapter — so candidates
    are filtered BEFORE fusion, never after."""
    def __init__(self, chunks: list[tuple]):
        self._chunks = [(c[0], c[1], c[2]) for c in chunks]
        self._payloads: dict[tuple[int, int], dict] = {
            (c[0], c[1]): (c[3] if len(c) > 3 else {}) for c in chunks
        }
        self._df: dict[str, int] = {}
        for _, _, text in self._chunks:
            for tok in set(_tokens(text)):
                self._df[tok] = self._df.get(tok, 0) + 1
        self._n = max(1, len(self._chunks))

    @staticmethod
    def _matches(payload: dict, nfilters: dict) -> bool:
        for key, want in nfilters.items():
            have = payload.get(key, "")
            if isinstance(want, list):
                if have not in want:
                    return False
            elif have != want:
                return False
        return True

    def _dense(self, q: list[str], text: str) -> float:
        t = set(_tokens(text)); qs = set(q)
        return len(qs & t) / (len(qs | t) or 1)

    def _sparse(self, q: list[str], text: str) -> float:
        toks = _tokens(text); score = 0.0
        for term in q:
            tf = toks.count(term)
            if tf:
                idf = math.log(1 + self._n / (1 + self._df.get(term, 0)))
                score += idf * (tf / (1 + len(toks)))
        return score

    def hybrid_search(self, query: str, query_vector, top_k, filters=None) -> list[RetrievedChunk]:
        from app.services.metadata_contract import normalize_filters
        q = _tokens(query)
        # Apply metadata filters AT retrieval (before fusion), exactly like the real Qdrant adapter.
        nfilters = normalize_filters(filters)
        pool = (self._chunks if not nfilters
                else [c for c in self._chunks if self._matches(self._payloads.get((c[0], c[1]), {}), nfilters)])
        dense = sorted(pool, key=lambda c: self._dense(q, c[2]), reverse=True)
        sparse = sorted(pool, key=lambda c: self._sparse(q, c[2]), reverse=True)
        # Reciprocal Rank Fusion over the two filtered candidate lists.
        rrf: dict[tuple[int, int], float] = {}
        k = 60
        for rank, c in enumerate(dense):
            rrf[(c[0], c[1])] = rrf.get((c[0], c[1]), 0.0) + 1.0 / (k + rank)
        for rank, c in enumerate(sparse):
            rrf[(c[0], c[1])] = rrf.get((c[0], c[1]), 0.0) + 1.0 / (k + rank)
        text_by_id = {(c[0], c[1]): c[2] for c in self._chunks}
        fused = sorted(rrf.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
        return [RetrievedChunk(d, ch, text_by_id[(d, ch)], s) for (d, ch), s in fused]


class MockReRanker(ReRanker):
    def rerank(self, query: str, chunks, top_k) -> list[RetrievedChunk]:
        q = set(_tokens(query))
        def score(c: RetrievedChunk) -> float:
            t = set(_tokens(c.text))
            return len(q & t) + 0.01 * c.score  # cross-encoder proxy
        return sorted(chunks, key=score, reverse=True)[:top_k]


class MockLLM(LLM):
    """Grounded mock: returns the top retrieved chunk verbatim (no hallucination, citation-aligned)."""
    def generate(self, query: str, context: list[str]) -> str:
        return context[0] if context else "I could not find a grounded answer for that."


class MockMarketData(MarketDataProvider):
    def _seed(self, symbol: str) -> float:
        h = int(hashlib.sha256(symbol.upper().encode()).hexdigest(), 16)
        return round(50 + (h % 95000) / 100.0, 2)

    def get_ltp(self, symbol: str) -> dict:
        ltp = self._seed(symbol)
        return {"symbol": symbol.upper(), "ltp": ltp, "currency": "INR", "source": "mock-market"}

    def get_ohlc(self, symbol: str) -> dict:
        base = self._seed(symbol)
        return {"symbol": symbol.upper(), "open": base, "high": round(base * 1.02, 2),
                "low": round(base * 0.98, 2), "close": round(base * 1.005, 2), "source": "mock-market"}

    def get_market_depth(self, symbol: str) -> dict:
        """Deterministic 5-level order book around the last traded price."""
        ltp = self._seed(symbol)
        tick = round(ltp * 0.0005 + 0.05, 2)
        bids = [{"price": round(ltp - tick * i, 2), "qty": 100 * i} for i in range(1, 6)]
        asks = [{"price": round(ltp + tick * i, 2), "qty": 100 * i} for i in range(1, 6)]
        return {"symbol": symbol.upper(), "ltp": ltp, "bids": bids, "asks": asks,
                "source": "mock-market"}

    def get_option_chain(self, symbol: str) -> dict:
        """Deterministic option chain: ATM-centred strikes with synthetic call/put quotes."""
        ltp = self._seed(symbol)
        step = max(1.0, round(ltp * 0.01, 0))
        atm = round(ltp / step) * step
        strikes = []
        for i in range(-2, 3):
            strike = round(atm + i * step, 2)
            strikes.append({
                "strike": strike,
                "call_ltp": round(max(0.05, ltp - strike) + step, 2),
                "put_ltp": round(max(0.05, strike - ltp) + step, 2),
            })
        return {"symbol": symbol.upper(), "underlying": ltp, "strikes": strikes,
                "source": "mock-market"}

    def subscribe_ticks(self, symbol: str, count: int = 1) -> list[dict]:
        """Deterministic snapshot stream stand-in for a real WebSocket subscription."""
        base = self._seed(symbol)
        return [{"symbol": symbol.upper(), "seq": i,
                 "ltp": round(base + (i % 5) * 0.05, 2), "source": "mock-market"}
                for i in range(max(1, count))]
