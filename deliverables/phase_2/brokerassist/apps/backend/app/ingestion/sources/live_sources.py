"""Live source adapters (opt-in) — real crawl / NSE / BSE / NALCO IR / Google Drive.

These are gated behind ``BA_INGEST_LIVE=true`` and require per-source configuration (URLs / Drive
credentials) plus optional network/parsing dependencies (see ``requirements-ingest.txt``). They are
deliberately NOT exercised on the default mocks-first path: with the flag off, ``base.get_source``
never constructs them, so CI stays credential- and network-free.

Each adapter raises a clear error when its endpoint/credentials are missing, rather than silently
falling back — keeping the live path explicit. Network fetching itself is left as a thin, well-marked
seam so wiring a real crawler (Crawl4AI / Playwright / Google Drive API) is a localized change."""
from __future__ import annotations

from app.config import settings
from app.ingestion.base import IngestionSource, RawDocument


class LiveSourceNotConfigured(RuntimeError):
    """A live source is enabled (BA_INGEST_LIVE) but its endpoint/credentials are missing."""


class _BaseLiveSource(IngestionSource):
    mode = "live"
    endpoint_setting = ""   # which settings attr must be non-empty
    human_name = ""

    def __init__(self, name: str):
        self.name = name

    def _require_endpoint(self) -> str:
        value = getattr(settings, self.endpoint_setting, "") if self.endpoint_setting else ""
        if not value:
            raise LiveSourceNotConfigured(
                f"{self.human_name}: set BA_{self.endpoint_setting.upper()} to enable live ingestion")
        return value

    def discover(self) -> list[RawDocument]:  # pragma: no cover - real network, off by default
        endpoint = self._require_endpoint()
        raise NotImplementedError(
            f"{self.human_name} live fetch from {endpoint!r} is not wired yet — implement the real "
            f"crawler/API call here. Until then run with BA_INGEST_LIVE=false (fixtures).")


class BrokerSiteLive(_BaseLiveSource):
    endpoint_setting = "broker_site_url"
    human_name = "Broker website crawler"


class NseLive(_BaseLiveSource):
    endpoint_setting = "nse_base_url"
    human_name = "NSE corporate filings"


class BseLive(_BaseLiveSource):
    endpoint_setting = "bse_base_url"
    human_name = "BSE filings"


class NalcoIrLive(_BaseLiveSource):
    endpoint_setting = "nalco_ir_url"
    human_name = "NALCO Investor Relations"


class GDriveLive(_BaseLiveSource):
    endpoint_setting = "gdrive_folder_id"
    human_name = "Google Drive knowledge repository"


_LIVE = {
    "broker_site": BrokerSiteLive,
    "nse": NseLive,
    "bse": BseLive,
    "nalco_ir": NalcoIrLive,
    "gdrive": GDriveLive,
}


def get_live_source(name: str) -> IngestionSource:
    cls = _LIVE.get(name)
    if cls is None:
        raise ValueError(f"no live adapter for source {name!r}")
    return cls(name)
