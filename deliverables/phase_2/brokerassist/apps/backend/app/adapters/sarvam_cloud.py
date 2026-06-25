"""Real Sarvam AI language adapter (detect + translate) — pulled into Phase 6 behind the existing
get_language() seam (the rest of Phase 7 — transliteration / STT / TTS — is out of scope here).

No model weights run in-process: this is a remote HTTPS call behind the LanguageProvider ABC.
Credential-gated (BA_SARVAM_API_KEY); the mocks-first path and CI stay credential-free.

Resilience (roadmap risk register): language work must never break the answer. On any failure,
`detect` falls back to a Unicode-script heuristic and `translate` returns the original text — both
logged — so a Sarvam outage degrades gracefully instead of erroring the request."""
from __future__ import annotations

import re
import time

from app.config import settings
from app.adapters.base import LanguageProvider
from app.core.observability import log

_RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504}

# Internal code (en/hi/ta) <-> Sarvam BCP-47-ish code (en-IN/hi-IN/ta-IN).
_TO_SARVAM = {"en": "en-IN", "hi": "hi-IN", "ta": "ta-IN"}

_DEVANAGARI = re.compile(r"[ऀ-ॿ]")
_TAMIL = re.compile(r"[஀-௿]")


def _script_detect(text: str) -> str:
    """Offline fallback detector (also used when Sarvam is unreachable)."""
    if _TAMIL.search(text):
        return "ta"
    if _DEVANAGARI.search(text):
        return "hi"
    return "en"


def _to_internal(code: str) -> str:
    base = (code or "en").split("-")[0].lower()
    return base if base in settings.supported_languages else "en"


class SarvamLanguage(LanguageProvider):
    def __init__(self, base_url: str | None = None, api_key: str | None = None,
                 timeout: int | None = None, retries: int | None = None):
        self.base_url = (base_url or settings.sarvam_base_url).rstrip("/")
        self.api_key = api_key or settings.sarvam_api_key
        self.timeout = timeout or settings.sarvam_timeout_seconds
        self.retries = settings.sarvam_retry_count if retries is None else retries
        if not self.api_key:
            raise RuntimeError("Sarvam not configured (set BA_SARVAM_API_KEY).")

    def _post(self, path: str, body: dict) -> dict:
        import httpx  # lazy import keeps the module importable without the dep present at rest

        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = {"api-subscription-key": self.api_key, "Content-Type": "application/json"}
        last_err: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                r = httpx.post(url, json=body, headers=headers, timeout=self.timeout)
                if r.status_code in _RETRYABLE_STATUS:
                    last_err = RuntimeError(f"retryable status {r.status_code}")
                    time.sleep(min(2 ** attempt, 8))
                    continue
                r.raise_for_status()
                return r.json()
            except Exception as e:  # network/timeout/transport — retry per policy
                last_err = e
                time.sleep(min(2 ** attempt, 8))
        raise RuntimeError(f"Sarvam {path} failed after {self.retries + 1} attempt(s): {last_err}")

    def detect(self, text: str) -> str:
        try:
            data = self._post("text-lid", {"input": text})
            code = data.get("language_code") or data.get("language") or ""
            return _to_internal(code) if code else _script_detect(text)
        except Exception as e:
            log.warning("Sarvam detect failed, using script heuristic: %s", e)
            return _script_detect(text)

    def translate(self, text: str, target: str, source: str | None = None) -> str:
        if not text or source == target:
            return text
        body = {
            "input": text,
            "source_language_code": _TO_SARVAM.get(source or "", "auto"),
            "target_language_code": _TO_SARVAM.get(target, "en-IN"),
        }
        try:
            data = self._post("translate", body)
            return data.get("translated_text") or text
        except Exception as e:
            log.warning("Sarvam translate failed, returning original text: %s", e)
            return text
