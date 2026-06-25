"""Phase 5 metadata contract — canonical normalization + validation for the Qdrant payload.

The Qdrant payload for `brokerage_kb` stores ONLY foreign keys + retrieval filters:
    document_id, chunk_id, language, company, filing_type, date
Citation fields (source, url, document_version, checksum) stay in PostgreSQL and are NEVER written
here. DocumentChunk carries `lang`; company/filing_type/date come from the parent Document — so the
payload is assembled by joining chunk -> document."""
from __future__ import annotations

from datetime import date as _date, datetime

from app.config import settings


class MetadataValidationError(ValueError):
    """Raised when a chunk's payload metadata violates the canonical contract (fail-fast)."""


# Synonyms mapped onto the canonical filing-type taxonomy (BA_METADATA_FILING_TYPES).
_FILING_SYNONYMS = {
    "dividend": "Corporate Action",
    "dividends": "Corporate Action",
    "result": "Quarterly Results",
    "results": "Quarterly Results",
    "quarterly result": "Quarterly Results",
    "annual": "Annual Report",
    "presentation deck": "Presentation",
    "press note": "Press Release",
    "faqs": "FAQ",
}

# Canonical company spellings.
_COMPANY_ALIASES = {
    "nalco": "NALCO",
    "national aluminium": "NALCO",
    "national aluminium company": "NALCO",
}


def normalize_language(lang: str | None) -> str:
    """Canonical language code; empty -> 'en'. Raises on an unsupported code."""
    code = (lang or "en").strip().lower()
    if code not in settings.language_codes:
        raise MetadataValidationError(
            f"unsupported language {code!r}; allowed: {settings.language_codes}")
    return code


def normalize_company(company: str | None) -> str:
    """Canonical company spelling. Empty is allowed (no company filter)."""
    name = (company or "").strip()
    if not name:
        return ""
    return _COMPANY_ALIASES.get(name.lower(), name)


def normalize_filing_type(filing_type: str | None, strict: bool = True) -> str:
    """Map to the canonical filing-type taxonomy. Unknown -> raise (strict) / passthrough (lenient)."""
    ft = (filing_type or "").strip()
    if not ft:
        if strict:
            raise MetadataValidationError("filing_type is required")
        return ""
    for canon in settings.filing_types:
        if ft.lower() == canon.lower():
            return canon
    if ft.lower() in _FILING_SYNONYMS:
        return _FILING_SYNONYMS[ft.lower()]
    if strict:
        raise MetadataValidationError(
            f"unknown filing_type {ft!r}; allowed: {settings.filing_types}")
    return ft


def normalize_date(value) -> str:
    """Normalize to ISO 'YYYY-MM-DD'. None/empty -> '' (allowed). Raises on a malformed string."""
    if value is None or value == "":
        return ""
    if isinstance(value, (datetime, _date)):
        return value.isoformat()[:10]
    s = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    raise MetadataValidationError(f"malformed date {value!r} (expected ISO YYYY-MM-DD)")


# Exactly the keys Qdrant is allowed to store (mirrors qdrant_real.PAYLOAD_CONTRACT).
PAYLOAD_KEYS = ("document_id", "chunk_id", "language", "company", "filing_type", "date")


def build_payload(*, document_id: int, chunk_id: int, language: str | None, company: str | None,
                  filing_type: str | None, filing_date, strict: bool = True) -> dict:
    """Assemble + validate the FK-only Qdrant payload from chunk/document fields."""
    payload = {
        "document_id": int(document_id),
        "chunk_id": int(chunk_id),
        "language": normalize_language(language),
        "company": normalize_company(company),
        "filing_type": normalize_filing_type(filing_type, strict=strict),
        "date": normalize_date(filing_date),
    }
    # Defensive: never let a citation field leak into the payload.
    extra = set(payload) - set(PAYLOAD_KEYS)
    if extra:
        raise MetadataValidationError(f"payload has disallowed keys: {sorted(extra)}")
    return payload
