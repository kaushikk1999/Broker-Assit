"""Ingestion source contract + factory.

A source ``discover()``s raw items; the orchestrator parses, extracts metadata, dedups/registers and
chunks them. The factory returns a deterministic offline *fixture* source by default and only returns a
*live* adapter when ``BA_INGEST_LIVE`` is set (and the live deps are present)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date

from app.config import settings

# The five ingestible knowledge sources (roadmap pp. 11-16). Source 2A (market data) is NOT here: it is
# a separate cached, non-Qdrant branch served by the Market Service and must never be crawled/ingested.
SOURCE_NAMES: tuple[str, ...] = ("broker_site", "nse", "bse", "nalco_ir", "gdrive")


@dataclass
class RawDocument:
    """One discovered item before parsing. ``content`` is raw (HTML/text/bytes); the orchestrator
    parses it to clean text. The metadata hints are canonicalized by ``metadata.extract``."""
    source: str
    url: str
    title: str
    content: object                      # str for text/html, bytes for binary formats
    content_type: str = "text/html"
    filing_type: str = ""
    filing_date: date | None = None
    company: str = ""
    lang: str = "en"


class IngestionSource(ABC):
    name: str = ""
    mode: str = "fixture"                 # "fixture" | "live"

    @abstractmethod
    def discover(self) -> list[RawDocument]:
        """Return the raw items to ingest. Fixture sources read deterministic offline data; live
        sources fetch over the network (only when BA_INGEST_LIVE is true)."""
        ...


def get_source(name: str) -> IngestionSource:
    """Resolve a source by name. Live adapter when BA_INGEST_LIVE, else the offline fixture source."""
    if name not in SOURCE_NAMES:
        raise ValueError(f"unknown ingestion source {name!r}; known: {SOURCE_NAMES}")
    if settings.ingest_live:
        from app.ingestion.sources.live_sources import get_live_source
        return get_live_source(name)
    from app.ingestion.sources.mock_sources import FixtureSource
    return FixtureSource(name)


def all_sources() -> list[IngestionSource]:
    return [get_source(n) for n in SOURCE_NAMES]
