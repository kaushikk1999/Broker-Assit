"""Test environment — set BEFORE any app import (pytest loads conftest first)."""
import os
import tempfile

os.environ.setdefault("BA_DATABASE_URL", f"sqlite:///{tempfile.gettempdir()}/ba_test.db")
# The in-memory rate-limit cache is shared across the process; keep the per-IP limiter from tripping
# across the whole suite (all calls share client ip 'testclient'). Per-session limit stays default.
os.environ.setdefault("BA_RATE_LIMIT_PER_IP_PER_MIN", "100000")
os.environ.setdefault("BA_ADMIN_SEED_PASSWORD", "admin12345")
# Tests are ALWAYS mocks-first and credential-free (invariant). Ignore any local developer `.env` so a
# filled-in .env (real vendor creds) can't flip the suite off the mocks-first path; config-default
# tests then see true defaults. use_mocks=true alone keeps every provider on its mock.
os.environ.setdefault("BA_DISABLE_DOTENV", "1")
os.environ.setdefault("BA_USE_MOCKS", "true")
os.environ.setdefault("BA_INGEST_LIVE", "false")
os.environ.setdefault("BA_QDRANT_URL", "")  # skip Qdrant network in tests

import pytest


@pytest.fixture
def mem_db():
    """An isolated in-memory SQLite session, so Phase 4 ingestion tests never pollute the shared test
    DB that the Phase 5/6 suites read from."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.db.base import Base
    from app.db import models  # noqa: F401 - populate metadata

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()
