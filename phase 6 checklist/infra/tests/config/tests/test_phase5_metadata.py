"""Phase 5 metadata contract: canonical normalization + validation for the FK-only payload."""
from datetime import date

import pytest

from app.services.metadata_contract import (
    normalize_language, normalize_company, normalize_filing_type, normalize_date,
    build_payload, MetadataValidationError, PAYLOAD_KEYS,
)


def test_language_ok_and_default():
    assert normalize_language("en") == "en"
    assert normalize_language("") == "en"
    assert normalize_language(None) == "en"
    assert normalize_language("HI") == "hi"


def test_language_invalid_rejected():
    with pytest.raises(MetadataValidationError):
        normalize_language("fr")


def test_company_normalization():
    assert normalize_company("nalco") == "NALCO"
    assert normalize_company(" National Aluminium ") == "NALCO"
    assert normalize_company("") == ""


def test_filing_type_canonical_and_synonym():
    assert normalize_filing_type("Board Meeting") == "Board Meeting"
    assert normalize_filing_type("financial results") == "Financial Results"
    assert normalize_filing_type("Dividend") == "Corporate Action"   # synonym mapping


def test_filing_type_invalid_rejected_strict():
    with pytest.raises(MetadataValidationError):
        normalize_filing_type("TotallyBogusType", strict=True)


def test_filing_type_lenient_passthrough():
    assert normalize_filing_type("TotallyBogusType", strict=False) == "TotallyBogusType"


def test_date_normalization():
    assert normalize_date(date(2025, 5, 15)) == "2025-05-15"
    assert normalize_date("2025-05-15") == "2025-05-15"
    assert normalize_date("15-05-2025") == "2025-05-15"
    assert normalize_date(None) == ""


def test_date_malformed_rejected():
    with pytest.raises(MetadataValidationError):
        normalize_date("not-a-date")


def test_build_payload_only_allowed_keys():
    p = build_payload(document_id=1, chunk_id=2, language="en", company="nalco",
                      filing_type="Dividend", filing_date=date(2025, 5, 16))
    assert set(p.keys()) == set(PAYLOAD_KEYS)
    assert p["company"] == "NALCO" and p["filing_type"] == "Corporate Action"
    # citation fields must NEVER appear in the payload
    for forbidden in ("url", "source", "document_version", "checksum", "title"):
        assert forbidden not in p
