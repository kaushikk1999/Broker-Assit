"""Deterministic text chunker (Phase 4 owns chunking; Phase 5 embeds the chunks).

Word-based sliding window using ``BA_CHUNK_SIZE`` / ``BA_CHUNK_OVERLAP`` (words). Deterministic and
offline — no model calls — so the same input always yields the same chunks (idempotent re-ingest)."""
from __future__ import annotations

import re

from app.config import settings

_WS = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Collapse whitespace so chunking is stable regardless of source formatting."""
    return _WS.sub(" ", (text or "").replace(" ", " ")).strip()


def chunk_text(text: str, *, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    """Split cleaned text into overlapping word windows.

    Returns ``[]`` for empty input, a single chunk when the text fits, and overlapping windows
    otherwise. ``overlap`` is clamped to ``< chunk_size`` so the window always advances."""
    size = chunk_size if chunk_size is not None else settings.chunk_size
    ov = overlap if overlap is not None else settings.chunk_overlap
    size = max(1, size)
    ov = max(0, min(ov, size - 1))

    words = normalize_text(text).split(" ")
    if words == [""]:
        return []
    if len(words) <= size:
        return [" ".join(words)]

    step = size - ov
    chunks: list[str] = []
    for start in range(0, len(words), step):
        window = words[start:start + size]
        if window:
            chunks.append(" ".join(window))
        if start + size >= len(words):
            break
    return chunks
