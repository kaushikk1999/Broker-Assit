"""Real cross-encoder re-ranker — a hosted cloud inference endpoint (e.g. BAAI/bge-reranker).

No reranker weights run in-process: this is a remote HTTPS call behind the ReRanker ABC, consistent
with the Ollama-Cloud-only constraint (no model weights on the FastAPI / Railway app). Credential-gated
(BA_RERANKER_URL); the mocks-first path and CI stay credential-free.

Resilience: the reranker is a precision booster, not a correctness gate. If the endpoint is unreachable
and BA_RERANK_FALLBACK_ENABLED is on, we degrade gracefully to the incoming RRF order (Top-k) rather
than failing the whole answer."""
from __future__ import annotations

import time

from app.config import settings
from app.adapters.base import ReRanker, RetrievedChunk
from app.core.observability import log

_RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504}


class HostedReRanker(ReRanker):
    def __init__(self, url: str | None = None, api_key: str | None = None,
                 model: str | None = None, timeout: int | None = None, retries: int | None = None):
        self.url = (url or settings.reranker_url).rstrip("/")
        self.api_key = api_key or settings.reranker_api_key
        self.model = model or settings.reranker_model
        self.timeout = timeout or settings.reranker_timeout_seconds
        self.retries = settings.reranker_retry_count if retries is None else retries
        if not self.url:
            raise RuntimeError("Hosted re-ranker not configured (set BA_RERANKER_URL).")

    def _score(self, query: str, documents: list[str]) -> list[float]:
        """POST query + documents, return one relevance score per document (input order preserved)."""
        import httpx  # lazy import keeps the module importable without the dep present at rest

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        body = {"model": self.model, "query": query, "documents": documents}
        last_err: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                r = httpx.post(self.url, json=body, headers=headers, timeout=self.timeout)
                if r.status_code in _RETRYABLE_STATUS:
                    last_err = RuntimeError(f"retryable status {r.status_code}")
                    time.sleep(min(2 ** attempt, 8))
                    continue
                r.raise_for_status()
                return _parse_scores(r.json(), len(documents))
            except Exception as e:  # network/timeout/transport/parse — retry per policy
                last_err = e
                time.sleep(min(2 ** attempt, 8))
        raise RuntimeError(f"re-ranker failed after {self.retries + 1} attempt(s): {last_err}")

    def rerank(self, query: str, chunks: list[RetrievedChunk], top_k: int) -> list[RetrievedChunk]:
        if not chunks:
            return []
        try:
            scores = self._score(query, [c.text for c in chunks])
        except Exception as e:
            if settings.rerank_fallback_enabled:
                # Degrade to the incoming RRF order (candidates arrive already fused/sorted).
                log.warning("reranker unavailable, falling back to RRF order: %s", e)
                return list(chunks)[:top_k]
            raise
        ranked = sorted(zip(chunks, scores), key=lambda cs: cs[1], reverse=True)
        out: list[RetrievedChunk] = []
        for chunk, score in ranked[:top_k]:
            chunk.score = float(score)  # surface the cross-encoder score downstream
            out.append(chunk)
        return out


def _parse_scores(data, n: int) -> list[float]:
    """Accept the common hosted-reranker response shapes and return n scores in input order.

    Supported: {"scores": [...]}, {"results": [{"index": i, "score": s}, ...]} (any order),
    {"data": [{"index": i, "relevance_score": s}, ...]}, or a bare list of scores/objects."""
    rows = data
    if isinstance(data, dict):
        if "scores" in data:
            scores = list(data["scores"])
            if len(scores) != n:
                raise RuntimeError(f"reranker returned {len(scores)} scores for {n} documents")
            return [float(s) for s in scores]
        rows = data.get("results") or data.get("data") or []
    if not isinstance(rows, list) or not rows:
        raise RuntimeError(f"unrecognized reranker response: keys={list(data) if isinstance(data, dict) else type(data)}")
    # list form: either bare numbers, or objects carrying an index + score.
    if all(isinstance(x, (int, float)) for x in rows):
        if len(rows) != n:
            raise RuntimeError(f"reranker returned {len(rows)} scores for {n} documents")
        return [float(x) for x in rows]
    scores = [0.0] * n
    for i, row in enumerate(rows):
        idx = row.get("index", i)
        val = row.get("score", row.get("relevance_score"))
        if val is None or not (0 <= idx < n):
            raise RuntimeError(f"malformed reranker row: {row}")
        scores[idx] = float(val)
    return scores
