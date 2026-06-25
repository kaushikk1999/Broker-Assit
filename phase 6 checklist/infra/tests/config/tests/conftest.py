"""Test environment — set BEFORE any app import (pytest loads conftest first)."""
import os
import tempfile

os.environ.setdefault("BA_DATABASE_URL", f"sqlite:///{tempfile.gettempdir()}/ba_test.db")
# The in-memory rate-limit cache is shared across the process; keep the per-IP limiter from tripping
# across the whole suite (all calls share client ip 'testclient'). Per-session limit stays default.
os.environ.setdefault("BA_RATE_LIMIT_PER_IP_PER_MIN", "100000")
os.environ.setdefault("BA_ADMIN_SEED_PASSWORD", "admin12345")
os.environ.setdefault("BA_QDRANT_URL", "")  # skip Qdrant network in tests
