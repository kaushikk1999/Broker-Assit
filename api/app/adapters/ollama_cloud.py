"""Real embedding provider — Ollama Cloud · embeddinggemma (multilingual EN/HI/TA).

No local model weights run in-process: this is a remote HTTPS call behind the EmbeddingProvider ABC.
Credential-gated — only used when BA_USE_MOCKS=false and BA_OLLAMA_CLOUD_URL/API_KEY are set, so the
mocks-first path and CI stay credential-free. Dimension is detected via probe_dimension() (inherited),
never hardcoded."""
from __future__ import annotations

import time

from app.config import settings
from app.adapters.base import EmbeddingProvider, LLM

_RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504}


class OllamaCloudEmbedding(EmbeddingProvider):
    def __init__(self, base_url: str | None = None, api_key: str | None = None,
                 model: str | None = None, timeout: int | None = None, retries: int | None = None):
        # Embeddings may target a different Ollama server than generation (e.g. a local sidecar running
        # qwen3-embedding) — BA_OLLAMA_EMBED_URL overrides, else fall back to the shared cloud URL.
        self.base_url = (base_url or settings.ollama_embed_url or settings.ollama_cloud_url).rstrip("/")
        self.api_key = api_key or settings.ollama_cloud_api_key
        self.model = model or settings.embedding_model
        self.timeout = timeout or settings.embedding_timeout_seconds
        self.retries = settings.embedding_retry_count if retries is None else retries
        if not self.base_url:
            raise RuntimeError(
                "Ollama embedding endpoint not configured (set BA_OLLAMA_EMBED_URL or BA_OLLAMA_CLOUD_URL).")

    def _post(self, inputs):
        import httpx  # lazy import keeps the module importable without the dep present at rest

        url = f"{self.base_url}/api/embed"
        headers = {"Content-Type": "application/json"}
        if self.api_key:  # a local Ollama sidecar needs no key; cloud does
            headers["Authorization"] = f"Bearer {self.api_key}"
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

    def embed(self, text: str, is_query: bool = False) -> list[float]:
        return self._post(text)[0]

    def embed_batch(self, texts: list[str], is_query: bool = False) -> list[list[float]]:
        if not texts:
            return []
        return self._post(texts)


# ----------------------------------------------------------------------- Gemma generation (Phase 6)
_SYSTEM_PROMPT = (
    "You are BrokerAssist, a stock-brokerage assistant. Answer the user's question using ONLY the "
    "numbered context passages provided. If the context does not contain the answer, say you don't have "
    "that information rather than guessing. Be concise and factual. This is informational only and not "
    "investment advice. Do not fabricate figures, dates, or sources."
)


def build_grounded_prompt(query: str, context: list[str]) -> tuple[str, str]:
    """Return (system, user) messages for grounded, citation-aligned generation. The context passages
    are the Top-5 reranked chunks; the model must answer only from them."""
    numbered = "\n\n".join(f"[{i + 1}] {c}" for i, c in enumerate(context)) or "(no context)"
    user = f"Context passages:\n{numbered}\n\nQuestion: {query}\n\nAnswer using only the context above."
    return _SYSTEM_PROMPT, user


class OllamaCloudLLM(LLM):
    """Ollama Cloud · Gemma generation. No local weights — remote HTTPS call behind the LLM ABC.
    Reuses the embedding account's base URL + API key; the model is BA_OLLAMA_GEN_MODEL."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None,
                 model: str | None = None, timeout: int | None = None, retries: int | None = None):
        self.base_url = (base_url or settings.ollama_cloud_url).rstrip("/")
        self.api_key = api_key or settings.ollama_cloud_api_key
        self.model = model or settings.ollama_gen_model
        self.timeout = timeout or settings.gen_timeout_seconds
        self.retries = settings.gen_retry_count if retries is None else retries
        if not self.base_url or not self.api_key:
            raise RuntimeError(
                "Ollama Cloud not configured (set BA_OLLAMA_CLOUD_URL and BA_OLLAMA_CLOUD_API_KEY).")

    def _post(self, system: str, user: str) -> str:
        import httpx  # lazy import keeps the module importable without the dep present at rest

        url = f"{self.base_url}/api/chat"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        body = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "stream": False,
            "options": {"temperature": settings.gen_temperature, "num_predict": settings.gen_max_tokens},
        }
        last_err: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                r = httpx.post(url, json=body, headers=headers, timeout=self.timeout)
                if r.status_code in _RETRYABLE_STATUS:
                    last_err = RuntimeError(f"retryable status {r.status_code}")
                    time.sleep(min(2 ** attempt, 8))
                    continue
                r.raise_for_status()
                return _extract_text(r.json())
            except Exception as e:  # network/timeout/transport/parse — retry per policy
                last_err = e
                time.sleep(min(2 ** attempt, 8))
        raise RuntimeError(f"Ollama Cloud generate failed after {self.retries + 1} attempt(s): {last_err}")

    def generate(self, query: str, context: list[str]) -> str:
        system, user = build_grounded_prompt(query, context)
        return self._post(system, user)


def _extract_text(data: dict) -> str:
    """Pull the assistant text from /api/chat ({message:{content}}) or /api/generate ({response})."""
    if isinstance(data, dict):
        msg = data.get("message")
        if isinstance(msg, dict) and msg.get("content"):
            return msg["content"].strip()
        if data.get("response"):
            return str(data["response"]).strip()
    raise RuntimeError(f"no generated text in response keys={list(data) if isinstance(data, dict) else type(data)}")
