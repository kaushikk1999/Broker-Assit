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
    # broker_site/gdrive are still thin seams (nse/bse/nalco_ir are now wired). With its endpoint set,
    # an un-wired live source must refuse (NotImplementedError) rather than silently fetch.
    monkeypatch.setattr(settings, "gdrive_folder_id", "some-folder-id")
    src = get_source("gdrive")
    assert src.mode == "live"
    with pytest.raises((NotImplementedError, RuntimeError)):
        src.discover()


def test_nse_bse_nalco_live_adapters_are_wired(monkeypatch):
    """NSE + BSE + NALCO IR now resolve to real, network-backed adapters (not the NotImplementedError
    stub). We don't hit the network here — just assert the live adapter type is selected when gated on."""
    monkeypatch.setattr(settings, "ingest_live", True)
    from app.ingestion.sources.live_sources import NseLive, BseLive, NalcoIrLive
    assert isinstance(get_source("nse"), NseLive)
    assert isinstance(get_source("bse"), BseLive)
    assert isinstance(get_source("nalco_ir"), NalcoIrLive)


def test_live_broker_site_unconfigured_raises(monkeypatch):
    monkeypatch.setattr(settings, "ingest_live", True)
    monkeypatch.setattr(settings, "broker_site_url", "")
    from app.ingestion.sources.live_sources import LiveSourceNotConfigured
    with pytest.raises(LiveSourceNotConfigured):
        get_source("broker_site").discover()
