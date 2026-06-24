# Phase 0 — Owner Decision Signoff

_Decisions captured 2026-06-23. These decisions are authoritative inputs to Phase 0 (research framing)
and Phase 1 (UX design)._

## Required owner confirmations
- **Brokerage type:** Embeddable AI assistant **product** (we are not a brokerage). We build a
  multi-tenant widget that brokerages embed on their own websites.
- **Launch market:** India (English / Hindi / Tamil). Specific launch region (pan-India vs Tamil-Nadu /
  Tier-2-3 first) — **still open**, see Open Items.
- **Target audience:** **Brokerages (B2B buyers)** are the PRIMARY audience. End-investors who use the
  embedded widget are the SECONDARY audience.
- **Product positioning:** Multilingual (EN/HI/TA), citation-backed AI assistant that brokerages embed
  to deflect support load, explain filings/stocks, and guide investors — with Hindi+Tamil finance
  support no incumbent offers.
- **Tenant model:** **Multi-tenant SaaS.** Per-brokerage API key + domain allowlist (per roadmap Phase 3).
- **Priority objective:** Ship an embeddable widget SaaS; use NALCO as the proof/demo content; sell to
  brokerages. (Pricing/monetization model deferred — see Open Items.)

## Signoff status
| Decision | Value | Approved By | Date | Notes |
|---|---|---|---|---|
| Brokerage type | Embeddable AI assistant product (not a brokerage) | Owner | 2026-06-23 | Multi-tenant widget SaaS |
| Launch market | India · EN/HI/TA | Owner | 2026-06-23 | Region focus TBD |
| Target audience | Brokerages (B2B buyers) primary; end-investors secondary | Owner | 2026-06-23 | Drives buyer-first personas |
| Product positioning | Multilingual, citation-backed embeddable assistant | Owner | 2026-06-23 | Hindi+Tamil = key wedge |
| Tenant model | Multi-tenant SaaS (API key + domain allowlist) | Owner | 2026-06-23 | Matches Phase 3 |
| Priority objective | Widget SaaS w/ NALCO demo; sell to brokerages | Owner | 2026-06-23 | — |
| Research scope | Public web + screenshots (no logins/paid tools) | Owner | 2026-06-23 | Drives #19 |
| Pricing page | Deferred from Phase 1 | Owner | 2026-06-23 | Nav reserves a slot |

## Open items (lower-priority, do not block Phase 0/1 start)
- Launch region: pan-India vs Tamil-Nadu / Tier-2-3 first (synthetic broker list hints at the latter).
- Business/pricing model (blocks the Pricing page only).
- NALCO content sources (NALCO Intelligence demo may use illustrative/sample data until provided).
- Role of `Brokerage List.xlsx` (target-market model vs KB seed vs test fixture).
- Drift replacement benchmark (Drift is being sunset).
