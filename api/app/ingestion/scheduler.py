"""Scheduler abstraction for ingestion cadences (P4-D3).

Phase 4 ships *run-once* commands (testable offline now). The recurring cadences (cron) are configured
here and are meant to be wired in the Railway **worker** service only — never the web process, so the
request path makes no live fetches. This module parses/validates the configured crons and exposes the
source -> cadence map; actually arming a scheduler (APScheduler/cron) is a worker-deployment concern."""
from __future__ import annotations

from dataclasses import dataclass

from app.config import settings
from app.ingestion.base import SOURCE_NAMES


@dataclass
class Cadence:
    source: str
    cron: str
    fields: tuple[str, str, str, str, str]  # minute hour dom month dow


class InvalidCronError(ValueError):
    """A configured cron cadence is not a valid 5-field expression."""


def parse_cron(expr: str) -> tuple[str, str, str, str, str]:
    """Validate a standard 5-field cron expression and return its fields. Raises on malformed input."""
    parts = (expr or "").split()
    if len(parts) != 5:
        raise InvalidCronError(f"cron must have 5 fields (got {len(parts)}): {expr!r}")
    return tuple(parts)  # type: ignore[return-value]


def cadences() -> list[Cadence]:
    """All configured source cadences (validated). Order follows ``SOURCE_NAMES``."""
    mapping = settings.ingest_cadences
    out: list[Cadence] = []
    for name in SOURCE_NAMES:
        cron = mapping[name]
        out.append(Cadence(source=name, cron=cron, fields=parse_cron(cron)))
    return out


def cadence_for(source: str) -> Cadence:
    if source not in SOURCE_NAMES:
        raise ValueError(f"unknown source {source!r}")
    cron = settings.ingest_cadences[source]
    return Cadence(source=source, cron=cron, fields=parse_cron(cron))
