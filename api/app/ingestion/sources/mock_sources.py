"""Fixture sources — deterministic, offline ``discover()`` over the bundled corpus (mocks-first).

Used whenever ``BA_INGEST_LIVE`` is false (the default), so the whole Phase 4 pipeline runs in CI and
locally with no credentials and no network."""
from __future__ import annotations

from app.ingestion.base import IngestionSource, RawDocument
from app.ingestion.fixtures import FIXTURES


class FixtureSource(IngestionSource):
    mode = "fixture"

    def __init__(self, name: str):
        self.name = name

    def discover(self) -> list[RawDocument]:
        items = FIXTURES.get(self.name, [])
        return [
            RawDocument(
                source=self.name,
                url=item["url"],
                title=item.get("title", ""),
                content=item["content"],
                content_type=item.get("content_type", "text/html"),
                filing_type=item.get("filing_type", ""),
                filing_date=item.get("filing_date"),
                company=item.get("company", ""),
                lang=item.get("lang", "en"),
            )
            for item in items
        ]
