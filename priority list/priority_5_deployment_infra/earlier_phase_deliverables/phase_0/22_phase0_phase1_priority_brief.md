# Phase 0 → Phase 1 Priority Brief

_The handoff from research to UX design. Translates the gap report into concrete Phase 1 priorities._

## Inputs to Phase 1
- **Positioning:** Multilingual (EN/HI/TA), citation-backed, embeddable finance assistant — the
  intersection no competitor occupies.
- **Audience:** PRIMARY = brokerage buyers (product/growth, compliance, support/ops leads); SECONDARY =
  end-investors using the embedded widget.
- **Three proof pillars to demo:** stock info, NALCO/filing intelligence, algo education — each shown
  with **citations** and **language switching**.
- **The site is B2B marketing + live demo:** every capability page must let a buyer *try the assistant*,
  not just read about it.

## Priority pages (build/wireframe order)
1. **Home** — positioning, the 4 differentiators, embedded live-demo widget, primary CTA (Book a demo).
2. **Contact** — primary B2B conversion (Book a demo / Request access + API key). Highest-value action.
3. **Stock Research** — capability demo: ask about a stock, get cited answer in EN/HI/TA.
4. **NALCO Intelligence** — capability demo: explain a filing/disclosure with citations.
5. **Algo Education** — capability demo: SEBI/NSE algo rules explained (seed data already provided).
6. _(Pricing — deferred; nav reserves a "coming soon" slot.)_

## Priority journeys
- **Buyer evaluation:** Home → see differentiators → try live demo on a capability page → Contact
  (book demo / request access). _Primary funnel._
- **End-investor (shown inside demo):** open widget → ask stock/filing/algo question → read cited
  answer → switch language → escalate to human if needed.

## Priority CTAs
- Primary: **Book a demo** / **Request access (get API key)** (Contact).
- Secondary: **Try the assistant** (opens the widget on every capability page).
- Tertiary: **See it in your language** (EN/HI/TA switch), **Talk to a human** (escalation).

## Multilingual implications
- Language switcher is a **first-class, global** control (header + inside widget), not buried.
- Demo answers must render correctly in Devanagari + Tamil scripts (fonts, line-height, truncation).
- Show **citations in every language** — this is the trust differentiator; must survive translation.
- Buyer-facing marketing copy primarily English, but capability demos must showcase HI/TA to prove the
  wedge. Plan label translation vs transliteration rules (see Phase 1 `26_language_behavior_matrix`).

## Open questions (carried into Phase 1)
- Launch region (pan-India vs Tamil-Nadu/Tier-2-3 first) — affects which language leads in demos.
- NALCO content sources — NALCO Intelligence demo may use illustrative/sample data until provided.
- Pricing/business model — gates the deferred Pricing page.
- Brand/visual direction — none defined yet; set in `28_visual_reference_board`.
