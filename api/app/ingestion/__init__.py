"""Phase 4 — Data Ingestion Layer.

Turns the six external knowledge sources into clean, deduplicated, registered, **chunked** documents in
PostgreSQL — ready for Phase 5 to embed into Qdrant. Phase 4 stops *before* embeddings/Qdrant writes
(seam P4-D1). Market data (Source 2A) is a separate cached, non-Qdrant branch and is never ingested
here.

Mocks-first: the full pipeline runs on deterministic offline fixtures (no credentials, no network). Real
crawl / NSE / BSE / NALCO-IR / Google-Drive adapters are gated behind ``BA_INGEST_LIVE`` (default off).
"""
