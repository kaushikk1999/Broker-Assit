"""Phase 4 sources — fixture discovery (default) and the gated live adapters."""
import pytest

from app.config import settings
from app.ingestion.base import SOURCE_NAMES, RawDocument, all_sources, get_source
from app.ingestion.sources.mock_sources import FixtureSource


def test_default_source_is_offline_fixture():
    src = get_source("nse")
    assert isinstance(src, FixtureSource) and src.mode == "fixture"
    docs = src.discover()
    assert docs and all(isinstance(d, RawDocument) and d.source == "nse" for d in docs)


def test_all_five_knowledge_sources_discover_items():
    assert set(SOURCE_NAMES) == {"broker_site", "nse", "bse", "nalco_ir", "gdrive"}
    # Market data (Source 2A) is intentionally NOT an ingestible source.
    assert "market" not in SOURCE_NAMES
    total = sum(len(s.discover()) for s in all_sources())
    assert total >= 5


def test_unknown_source_raises():
    with pytest.raises(ValueError):
        get_source("twitter")


def test_live_adapter_is_gated_and_refuses_without_wiring(monkeypatch):
    monkeypatch.setattr(settings, "ingest_live", True)
    src = get_source("nse")
    assert src.mode == "live"
    # The live path is deliberately not wired (mocks-first): it must refuse rather than silently fetch.
    with pytest.raises((NotImplementedError, RuntimeError)):
        src.discover()


def test_live_broker_site_unconfigured_raises(monkeypatch):
    monkeypatch.setattr(settings, "ingest_live", True)
    monkeypatch.setattr(settings, "broker_site_url", "")
    from app.ingestion.sources.live_sources import LiveSourceNotConfigured
    with pytest.raises(LiveSourceNotConfigured):
        get_source("broker_site").discover()
