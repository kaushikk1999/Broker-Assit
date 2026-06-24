# Phase 0 — Final Gap Report

_Based on `competitors_final.csv` + `feature_matrix_final.csv` (10 competitors: 5 Indian brokers,
5 AI platforms). Scope: public web + screenshots. Scores 0–5; unverified items honestly flagged._

## Summary
No incumbent combines the four things this product proposes: **(1) deep multilingual finance support
(Hindi + Tamil), (2) source-cited answers, (3) finance-domain depth (stocks, filings, NALCO, algo),
and (4) easy website embeddability.** Indian brokers have strong *stock information* (all score 5) but
weak/zero *filing explanation, citations, and Tamil support*. Generic AI platforms (Intercom/Fin,
Freshchat, Botpress) have strong *multilingual + RAG grounding + human handoff* but **zero finance
domain knowledge** out of the box. The opportunity is the **intersection** that nobody occupies.

### Feature-matrix highlights (total score / 75)
- Brokers: Upstox **22**, Zerodha 18, Groww 17, ICICI Direct 14, Angel One 13.
- AI platforms: Intercom/Fin **19**, Drift 19 (sunset), Botpress 18, Freshchat 17, ManyChat 16.
- Universal zeros across ALL 10: `filing_explanation`, `citations`, `multilingual_finance_support`
  (brokers) — i.e., the exact capabilities in our roadmap are unserved.

## Top gaps (what competitors are missing)
1. **No Hindi + Tamil finance assistant.** Best case is Angel One's *partial* Hindi KB articles. Tamil
   finance support is effectively absent across all 10. Generic platforms translate UI but have no
   finance content.
2. **No source citations.** Not a single competitor surfaces "here's the filing/circular this answer
   came from." Critical for a regulated, trust-sensitive finance audience.
3. **No filing / disclosure explanation.** Brokers give quotes and basic research; none explain
   corporate filings/disclosures in plain language (the NALCO use-case).
4. **Fragmented support UX.** Zerodha = tickets only (no chat); others split across app-only chatbots,
   WhatsApp bots, and phone with limited hours. No unified, embeddable, web-first assistant.
5. **No investor-education + algo-education layer** tied to the assistant.

## Differentiation opportunities (where WE win)
1. **Hindi + Tamil financial assistant** — the clear, defensible wedge; no incumbent covers Tamil
   finance. (Top differentiator AND top execution risk — Tamil terminology/transliteration.)
2. **Citations-first answers** — every response shows its source (filing, circular, KB doc).
3. **Finance-domain RAG depth** — stocks + filings + NALCO disclosure intelligence + algo education in
   one assistant.
4. **Drop-in embeddable widget** — one snippet, per-brokerage API key + domain allowlist; faster to
   adopt than building app-only bots (the brokers' current path).
5. **Reference UX to borrow:** Groww's public MCP (portfolio querying) and Upstox's WhatsApp
   account-activation flow are strong models for grounded, action-oriented assistance.

## Risks
1. **Tamil financial NLP quality** — terminology, transliteration, mixed-language input; heavy reliance
   on Sarvam AI. Biggest product risk.
2. **Regulatory/compliance** — finance answers + algo content are SEBI/NSE-sensitive; citations and
   disclaimers are mandatory, not optional.
3. **Competitive catch-up** — Intercom/Fin (45 langs) or Freshchat (60+ langs) could add finance
   content faster than a broker could add languages; our moat must be finance depth + citations + Tamil.
4. **Research blind spots** — app-only/login-gated competitor features remain "Not verified" (per
   public-only scope); avoid over-claiming gaps that may exist behind login.
5. **Drift sunset** — drop from active benchmarking; optionally add a live successor (e.g., 1mind) later.

## Methodology note
Findings rely on public sources + vendor case studies. Cells needing hands-on app/login access are
marked "Not verified" and should not be treated as confirmed gaps.
