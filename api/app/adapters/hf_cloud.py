"""Real embedding provider — Hugging Face Inference API (e.g., BAAI/bge-small-en-v1.5).

No local model weights run in-process: this is a remote HTTPS call behind the EmbeddingProvider ABC.
Credential-gated — only used when BA_USE_MOCKS=false and BA_HF_API_KEY is set.
"""
from __future__ import annotations

import time
from typing import Any

from app.config import settings
from app.adapters.base import EmbeddingProvider
from app.core.observability import log

_RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504}
_BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


class HuggingFaceEmbedding(EmbeddingProvider):
    def __init__(self, base_url: str | None = None, api_key: str | None = None,
                 model: str | None = None, timeout: int | None = None, retries: int | None = None):
        self.base_url = (base_url or settings.hf_api_base).rstrip("/")
        self.api_key = api_key or settings.hf_api_key
        self.model = model or settings.hf_embedding_model
        self.timeout = timeout or settings.embedding_timeout_seconds
        self.retries = settings.embedding_retry_count if retries is None else retries
        if not self.api_key:
            raise RuntimeError(
                "Hugging Face embedding endpoint not configured (set BA_HF_API_KEY).")

    def _post(self, inputs: str | list[str]) -> list[Any]:
        import httpx  # lazy import

        url = f"{self.base_url}/pipeline/feature-extraction/{self.model}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        body = {"inputs": inputs}
        
        last_err: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                r = httpx.post(url, json=body, headers=headers, timeout=self.timeout)
                if r.status_code == 503:
                    # HF Inference API spins down models when idle.
                    data = r.json()
                    if isinstance(data, dict) and "estimated_time" in data:
                        wait_time = data["estimated_time"]
                        log.info(f"HF Model {self.model} is loading. Waiting {wait_time:.2f} seconds...")
                        time.sleep(wait_time)
                        continue
                if r.status_code in _RETRYABLE_STATUS:
                    last_err = RuntimeError(f"retryable status {r.status_code}")
                    time.sleep(min(2 ** attempt, 8))
                    continue
                r.raise_for_status()
                data = r.json()
                if not isinstance(data, list):
                    raise RuntimeError(f"unexpected response type from HF: {type(data)} - {data}")
                return data
            except Exception as e:
                last_err = e
                time.sleep(min(2 ** attempt, 8))
        raise RuntimeError(
            f"Hugging Face Inference API embed failed after {self.retries + 1} attempt(s): {last_err}")

    def embed(self, text: str, is_query: bool = False) -> list[float]:
        # Prefix query strings if using a model that recommends it (like BGE)
        if is_query and "bge" in self.model.lower():
            text = f"{_BGE_QUERY_PREFIX}{text}"
            
        data = self._post(text)
        # For a single string input, HF returns a list of floats (the embedding).
        if data and isinstance(data[0], float):
            return data
        elif data and isinstance(data[0], list):
            # Sometimes it might return a nested list even for single inputs depending on API version.
            return data[0]
        raise RuntimeError(f"unexpected embedding format from HF: {data}")

    def embed_batch(self, texts: list[str], is_query: bool = False) -> list[list[float]]:
        if not texts:
            return []
            
        if is_query and "bge" in self.model.lower():
            texts = [f"{_BGE_QUERY_PREFIX}{t}" for t in texts]
            
        data = self._post(texts)
        # For a list of strings, HF returns a list of lists of floats.
        if data and isinstance(data[0], list):
            return data
        raise RuntimeError(f"unexpected batch embedding format from HF: {data}")
