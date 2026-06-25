# Phase 2 — Decisions Log (W0 discovery close-out)

| # | Decision | Value | Date | Source |
|---|---|---|---|---|
| D1 | Frontend strategy | Port Phase 1 prototype to Next.js (App Router) + extract embeddable widget | 2026-06-23 | Owner |
| D2 | Repo/deploy topology | Monorepo, multi-service on Railway | 2026-06-23 | Owner |
| D3 | Build scope | NALCO knowledge-RAG pilot thin-slice first; market + worker stubbed | 2026-06-23 | Owner |
| D4 | Vendor readiness | Mocks/stubs first behind clean interfaces; wire real vendors later | 2026-06-23 | Owner |
| D5 | Tenant model | Multi-tenant SaaS (public widget key + domain allowlist) | Phase 0/1 | Owner |
| D6 | Audience | B2B brokerages (primary); end-investors (secondary) | Phase 0/1 | Owner |
| D7 | Languages | English, Hindi, Tamil; query translated to EN before retrieval | Roadmap | Roadmap |
| D8 | Local DB | SQLite for dev; PostgreSQL for production (same SQLAlchemy models) | 2026-06-23 | Eng |
| D9 | Citations | Resolved from PostgreSQL Document Registry; Qdrant payload = FKs only | Roadmap | Roadmap |

## Still open (settle before production wiring)
- Qdrant hosting (Qdrant Cloud vs Railway-hosted).
- Hosted re-ranker provider/endpoint.
- Market-data vendor for production (roadmap: TrueData primary).
- Source-authority precedence on conflict (NSE vs BSE vs IR vs broker site).
- The remaining mandatory discovery inputs in `01_information_inventory_filled.md`.
