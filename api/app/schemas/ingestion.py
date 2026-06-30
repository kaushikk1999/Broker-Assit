"""Pydantic schemas for the Phase 4 ingestion admin endpoints."""
from __future__ import annotations

from pydantic import BaseModel


class SourceInfo(BaseModel):
    name: str
    mode: str          # "fixture" | "live"
    cron: str          # configured refresh cadence (wired in the worker only)


class IngestRequest(BaseModel):
    source: str | None = None   # ingest a single source…
    all: bool = False           # …or every source


class IngestionRunOut(BaseModel):
    id: int
    source: str
    mode: str
    status: str
    discovered: int
    registered: int
    versioned: int
    duplicates: int
    chunks_written: int
    errors: int
    started_at: str | None = None
    finished_at: str | None = None
