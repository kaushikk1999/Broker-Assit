# Phase 1 — Information Architecture & Sitemap

_B2B SaaS marketing + live-demo site selling the embeddable assistant to brokerages. Pricing deferred._

## Sitemap
```
Home (/)
├── Stock Research (/stock-research)        ← capability demo
├── NALCO Intelligence (/nalco)             ← capability demo
├── Algo Education (/algo-education)         ← capability demo
├── Contact (/contact)                      ← PRIMARY B2B conversion
└── [Pricing (/pricing)]                    ← DEFERRED (nav slot reserved, "coming soon")

Global (present on every page):
• Header: logo · nav · Language switcher (EN/HI/TA) · "Book a demo" button
• Floating Assistant widget (the product itself, in demo mode)
• Footer: company · compliance/disclaimer · contact · language switcher
```

## Page hierarchy (priority)
1. Home (entry + positioning) → 2. Contact (convert) → 3. Stock Research →
4. NALCO Intelligence → 5. Algo Education. (Pricing deferred.)

## Global navigation
- **Primary nav:** Home · Stock Research · NALCO Intelligence · Algo Education · Contact.
- **Persistent CTA:** "Book a demo" (top-right, all pages).
- **Language switcher:** header + footer + inside widget; EN / हिं / தமிழ். Selection persists across
  pages and into the widget.
- **Assistant entry:** floating launcher bottom-right on every page; "Try the assistant" buttons on
  capability pages open it pre-seeded with a relevant example query.

## IA principles
- **Two layers kept distinct:** (a) *marketing* content for buyers; (b) *live demo* of the assistant.
  Capability pages clearly label the demo ("This is the live assistant — try it").
- **Differentiators-first:** Home leads with the 4 wedges (Hindi+Tamil, citations, finance depth,
  embeddable).
- **One primary action per page**, funneling to Contact.
- **Citations + language** visible everywhere the assistant appears (the trust story).

## Content model (reusable blocks)
Hero · Differentiator card · Capability-demo panel (query → cited answer) · Citation/source chip ·
Logo/social proof · Stat callout · CTA band · Contact form · Compliance/disclaimer · Footer.
