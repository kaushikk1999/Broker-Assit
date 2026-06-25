"""Phase 6 query expansion — deterministic, additive, and a no-op for unknown terms."""
from app.services.query_expansion import expand_query


def test_expands_known_company_and_terms():
    out = expand_query("NALCO quarterly result")
    assert out.startswith("NALCO quarterly result")  # original preserved verbatim
    low = out.lower()
    assert "national aluminium" in low
    assert "quarterly results" in low


def test_noop_for_greeting():
    assert expand_query("hello there") == "hello there"


def test_deterministic():
    assert expand_query("NALCO dividend") == expand_query("NALCO dividend")


def test_does_not_duplicate_existing_phrase():
    out = expand_query("national aluminium results")
    # 'national aluminium' already present → not appended again
    assert out.lower().count("national aluminium") == 1


def test_disabled_returns_input(monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "query_expansion_enabled", False)
    assert expand_query("NALCO dividend") == "NALCO dividend"
