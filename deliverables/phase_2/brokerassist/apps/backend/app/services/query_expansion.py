"""Phase 6 query expansion — deterministic, provider-agnostic recall booster.

Runs on the English query (after translate-to-English) BEFORE embedding + sparse encoding. It appends
canonical domain synonyms for any known terms so dense and sparse retrieval also match documents that
use the corpus's phrasing (e.g. "NALCO" ~ "National Aluminium", "results" ~ "Quarterly Results").

Deterministic and dependency-free, so the mocks-first path stays credential-free and reproducible.
It is a NO-OP for queries with no known terms (e.g. greetings), which keeps the relevance gate honest
and never invents grounding. Expansion is used only for retrieval; the original question is what gets
reranked and sent to generation."""
from __future__ import annotations

import re

from app.config import settings

# term (matched case-insensitively as a whole lowercase word) -> canonical phrases to append.
_EXPANSIONS: dict[str, tuple[str, ...]] = {
    "nalco": ("national aluminium", "national aluminium company"),
    # NOTE: deliberately not "financial results" — that phrase collides with the Board-Meeting
    # document ("audited financial results") and would blur results-vs-board disambiguation.
    "result": ("quarterly results",),
    "results": ("quarterly results",),
    "earnings": ("quarterly results",),
    "dividend": ("corporate action", "interim dividend", "final dividend"),
    "dividends": ("corporate action", "interim dividend", "final dividend"),
    "board": ("board meeting", "board outcome"),
    "algo": ("algorithmic trading", "white box", "black box"),
    "algos": ("algorithmic trading", "white box", "black box"),
    "filing": ("disclosure", "corporate filing"),
    "filings": ("disclosure", "corporate filing"),
    "annual": ("annual report",),
}


def expand_query(query_en: str) -> str:
    """Return the query augmented with canonical synonyms for any known terms it contains.

    The original text is preserved verbatim; expansion phrases are appended once (deduped, and skipped
    if already present) so embedding and sparse encoding see both the user's phrasing and the corpus's
    canonical phrasing. Returns the input unchanged when expansion is disabled or nothing matches."""
    if not settings.query_expansion_enabled:
        return query_en
    low = query_en.lower()
    tokens = set(re.findall(r"[a-z]+", low))
    additions: list[str] = []
    seen: set[str] = set()
    for term, phrases in _EXPANSIONS.items():
        if term in tokens:
            for phrase in phrases:
                if phrase not in seen and phrase not in low:
                    additions.append(phrase)
                    seen.add(phrase)
    if not additions:
        return query_en
    return f"{query_en} {' '.join(additions)}"
