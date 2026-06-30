"""Metadata extraction — derive canonical Document fields from a discovered source item.

Reuses the Phase 5 metadata contract (``app.services.metadata_contract``) so the values Phase 4 writes
into PostgreSQL are exactly what Phase 5 will put in the Qdrant FK-only payload (company spelling,
filing-type taxonomy, ISO dates, supported language). The extractor GUARANTEES a canonical
``filing_type`` so the downstream strict payload build never rejects an ingested chunk."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from app.config import settings
from app.services.metadata_contract import (
    normalize_company, normalize_filing_type, normalize_language,
)

# Keyword -> canonical filing type, used to infer a type when the source gives none / a non-canonical one.
_KEYWORD_FILING_TYPE = [
    ("annual report", "Annual Report"),
    ("quarterly result", "Quarterly Results"),
    ("quarterly", "Quarterly Results"),
    ("financial result", "Financial Results"),
    ("shareholding", "Shareholding Pattern"),
    ("board meeting", "Board Meeting"),
    ("dividend", "Corporate Action"),
    ("corporate action", "Corporate Action"),
    ("buyback", "Corporate Action"),
    ("press release", "Press Release"),
    ("presentation", "Presentation"),
    ("investor", "Presentation"),
    ("faq", "FAQ"),
    ("how do i", "FAQ"),
    ("kyc", "FAQ"),
    ("open account", "FAQ"),
    ("pricing", "FAQ"),
    ("brokerage", "FAQ"),
    ("announcement", "Press Release"),
]
# Safe canonical fallback when nothing else matches (must be in BA_METADATA_FILING_TYPES).
_DEFAULT_FILING_TYPE = "Press Release"


@dataclass
class DocumentMeta:
    source: str
    url: str
    title: str
    company: str
    filing_type: str
    filing_date: date | None
    lang: str


def _to_date(value) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    s = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _canonical_filing_type(hint: str | None, title: str, text: str) -> str:
    """Map a (possibly missing / non-canonical) hint to the canonical taxonomy, inferring from
    title/text when needed, then falling back to a safe canonical default."""
    candidate = normalize_filing_type(hint, strict=False)
    if candidate in settings.filing_types:
        return candidate
    haystack = f"{title} {hint or ''} {text[:400]}".lower()
    for needle, canon in _KEYWORD_FILING_TYPE:
        if needle in haystack:
            return canon
    return _DEFAULT_FILING_TYPE


def extract(raw, text: str) -> DocumentMeta:
    """Build canonical metadata for a discovered item (``raw`` is a ``sources.base.RawDocument``)."""
    title = (raw.title or "").strip() or _derive_title(text)
    return DocumentMeta(
        source=raw.source,
        url=(raw.url or "").strip(),
        title=title[:300],
        company=normalize_company(raw.company),
        filing_type=_canonical_filing_type(raw.filing_type, title, text),
        filing_date=_to_date(raw.filing_date),
        lang=normalize_language(raw.lang),
    )


def _derive_title(text: str) -> str:
    """First non-empty sentence/line as a title fallback."""
    head = (text or "").strip().split(". ")[0]
    return head[:120] if head else "Untitled document"
