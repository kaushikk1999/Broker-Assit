"""Phase 4 scheduler config — cadences parse to valid crons (wired in the worker only, not the web)."""
import pytest

from app.config import settings
from app.ingestion.base import SOURCE_NAMES
from app.ingestion.scheduler import InvalidCronError, cadence_for, cadences, parse_cron


def test_every_source_has_a_valid_cron_cadence():
    cads = cadences()
    assert {c.source for c in cads} == set(SOURCE_NAMES)
    for c in cads:
        assert len(c.fields) == 5


def test_default_cadences_match_roadmap_refresh_schedule():
    assert settings.ingest_cadences["gdrive"] == "*/15 * * * *"   # every 15 minutes
    assert settings.ingest_cadences["nse"] == "0 * * * *"          # hourly
    assert settings.ingest_cadences["broker_site"].endswith("* * *")  # daily


def test_parse_cron_rejects_malformed():
    with pytest.raises(InvalidCronError):
        parse_cron("0 2 * *")        # only 4 fields
    with pytest.raises(InvalidCronError):
        parse_cron("")


def test_cadence_for_unknown_source_raises():
    with pytest.raises(ValueError):
        cadence_for("market")
