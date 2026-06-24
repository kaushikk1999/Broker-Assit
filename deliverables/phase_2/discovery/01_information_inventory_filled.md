# Phase 2 — Information Required Inventory (status)

Closing the 24 mandatory inputs from the discovery pack (`02_information_required_inventory.html`).
Confirmed = known from Phase 0/1/roadmap. TBD = owner confirmation still required (no invented values).

| Input | Status | Value / Note |
|---|---|---|
| Phase 2 scope | ✅ | NALCO knowledge-RAG pilot thin-slice + widget security; market/worker stubbed |
| Business objective | ✅ | Sell embeddable multilingual cited assistant to brokerages (B2B SaaS) |
| Primary success metrics | ⚠️ TBD | Proposed: support deflection %, cited-answer rate, EN/HI/TA coverage, demo→lead |
| Target customer segments | ✅ | Brokerages (buyers); end-investors (widget users) |
| Supported languages | ✅ | EN, HI, TA; query translated to EN before retrieval |
| Intents in scope | ✅ | market_data, filing/dividend/board, algo_education, knowledge_general |
| Out-of-scope behaviors | ✅ | No order execution; informational only + disclaimer on every answer |
| Pilot scope | ✅ | One company (NALCO), knowledge KB seeded, one demo tenant |
| Launch scope | ⚠️ TBD | Multi-tenant onboarding, real vendors, worker, market data |
| Tenant model | ✅ | Multi-tenant SaaS (widget key + domain allowlist) |
| Expected user volumes | ⚠️ TBD | Roadmap target 100+ concurrent; need avg/peak/burst figures |
| Latency target | ⚠️ TBD | Proposed: market < 800ms; knowledge < 4s p95 |
| Availability target | ⚠️ TBD | Proposed: 99.5% pilot |
| RPO / RTO | ⚠️ TBD | Owner to set (registry is the durable asset) |
| Budget ceiling | ⚠️ TBD | Needed to bound Ollama/Sarvam/market-data spend |
| Cost-control policy | ✅ (mechanism) | Per-tenant daily quota + per-session rate limit implemented; caps TBD |
| Data retention policy | ⚠️ TBD | Sessions/logs/analytics retention periods |
| Data deletion policy | ⚠️ TBD | Deletion workflow + authority |
| Data residency | ⚠️ TBD | India residency likely; constrains Qdrant/DB region |
| Security requirements | ✅ (baseline) | Widget key + Origin allowlist + signed session JWT + rate/quota |
| Compliance requirements | ⚠️ TBD | SEBI/NSE content disclaimers in place; legal review pending |
| Source authority rules | ⚠️ TBD | Precedence NSE/BSE/IR/site on conflict |
| Vendor approval status | ⚠️ TBD | Ollama Cloud, Sarvam, Qdrant, re-ranker host, TrueData — approvals/credentials |
| Operational ownership | ⚠️ TBD | Named owners for arch/ops/security/vendors |

**Gate:** none of the ⚠️ items block the **pilot thin-slice against mocks**; they block **production
vendor integration and launch**.
