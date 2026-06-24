"""Deterministic mock providers (mocks-first). Each implements a base interface so the real vendor
(Sarvam / Ollama Cloud / Qdrant / hosted re-ranker / TrueData) can drop in without touching callers."""
from __future__ import annotations
import hashlib
import math
import re

from app.adapters.base import (
    LanguageProvider, EmbeddingProvider, VectorStore, ReRanker, LLM,
    MarketDataProvider, RetrievedChunk,
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
    def embed(self, text: str) -> list[float]:
        h = hashlib.sha256(text.encode()).digest()
        return [b / 255.0 for b in h[:16]]  # deterministic stand-in vector


class MockVectorStore(VectorStore):
    """Dense (semantic proxy = token overlap) + sparse (BM25-lite IDF) → RRF, filtered at retrieval."""
    def __init__(self, chunks: list[tuple[int, int, str]]):
        self._chunks = chunks
        self._df: dict[str, int] = {}
        for _, _, text in chunks:
            for tok in set(_tokens(text)):
                self._df[tok] = self._df.get(tok, 0) + 1
        self._n = max(1, len(chunks))

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
        q = _tokens(query)
        dense = sorted(self._chunks, key=lambda c: self._dense(q, c[2]), reverse=True)
        sparse = sorted(self._chunks, key=lambda c: self._sparse(q, c[2]), reverse=True)
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
