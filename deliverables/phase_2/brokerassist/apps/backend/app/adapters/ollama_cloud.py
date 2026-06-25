"""Real embedding provider — Ollama Cloud · embeddinggemma (multilingual EN/HI/TA).

No local model weights run in-process: this is a remote HTTPS call behind the EmbeddingProvider ABC.
Credential-gated — only used when BA_USE_MOCKS=false and BA_OLLAMA_CLOUD_URL/API_KEY are set, so the
mocks-first path and CI stay credential-free. Dimension is detected via probe_dimension() (inherited),
never hardcoded."""
from __future__ import annotations

import time

from app.config import settings
from app.adapters.base import EmbeddingProvider

_RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504}


class OllamaCloudEmbedding(EmbeddingProvider):
    def __init__(self, base_url: str | None = None, api_key: str | None = None,
                 model: str | None = None, timeout: int | None = None, retries: int | None = None):
        self.base_url = (base_url or settings.ollama_cloud_url).rstrip("/")
        self.api_key = api_key or settings.ollama_cloud_api_key
        self.model = model or settings.embedding_model
        self.timeout = timeout or settings.embedding_timeout_seconds
        self.retries = settings.embedding_retry_count if retries is None else retries
        if not self.base_url or not self.api_key:
            raise RuntimeError(
                "Ollama Cloud not configured (set BA_OLLAMA_CLOUD_URL and BA_OLLAMA_CLOUD_API_KEY).")

    def _post(self, inputs):
        import httpx  # lazy import keeps the module importable without the dep present at rest

        url = f"{self.base_url}/api/embed"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        body = {"model": self.model, "input": inputs}
        last_err: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                r = httpx.post(url, json=body, headers=headers, timeout=self.timeout)
                if r.status_code in _RETRYABLE_STATUS:
                    last_err = RuntimeError(f"retryable status {r.status_code}")
                    time.sleep(min(2 ** attempt, 8))
                    continue
                r.raise_for_status()
                data = r.json()
                embs = data.get("embeddings")
                if embs is None and "embedding" in data:  # older single-vector shape
                    embs = [data["embedding"]]
                if not embs:
                    raise RuntimeError(f"no embeddings in response keys={list(data)}")
                return embs
            except Exception as e:  # network/timeout/transport — retry per policy
                last_err = e
                time.sleep(min(2 ** attempt, 8))
        raise RuntimeError(
            f"Ollama Cloud embed failed after {self.retries + 1} attempt(s): {last_err}")

    def embed(self, text: str) -> list[float]:
        return self._post(text)[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self._post(texts)
