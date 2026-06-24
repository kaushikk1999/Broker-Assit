# Phase 1 — User Journeys

## J1 — Buyer evaluation (PRIMARY funnel)
```
Land on Home (ad / referral / search)
  → Read positioning + 4 differentiators
  → "Try the assistant" → widget opens with example query
  → Visit a capability page (Stock Research / NALCO / Algo)
  → Ask a question → see CITED answer → switch to Hindi/Tamil → answer re-renders cited
  → Trust established → click "Book a demo"
  → Contact form (name, brokerage, size, use-case, language needs)
  → Confirmation + next steps (calendar / API-key request)
```
**Emotion arc:** curious → impressed (it actually works, cited) → convinced (it's my language) → act.
**Drop-off risks:** demo feels canned; citations unclear; language switch breaks layout. Mitigate with
real demo, prominent source chips, tested Indic typography.

## J2 — Compliance validation (PRIMARY, gating)
```
Compliance officer opens a capability page
  → Asks an edge question
  → Checks: Is there a citation? Is there a disclaimer? Can the source be opened?
  → Reviews how algo/finance content is governed
  → Approves vendor for demo
```
**Need:** every answer must show source + disclaimer; "View source" must open the actual doc/circular.

## J3 — End-investor: ask a stock question (SECONDARY, shown in demo)
```
Open widget → type/ask "What is X's latest result?" (or in Hindi/Tamil)
  → Assistant answers in plain language + citation chip
  → Investor taps citation → sees the filing/source
  → Optional: "Explain in Tamil" → re-rendered
```

## J4 — End-investor: understand a NALCO filing (SECONDARY)
```
NALCO Intelligence page → "Explain NALCO's latest disclosure"
  → Plain-language summary + key figures + citation to the disclosure
  → Follow-up Q&A
```

## J5 — End-investor: learn algo basics (SECONDARY)
```
Algo Education page → "What's the difference between white-box and black-box algos?"
  → Cited explanation (NSE FAQ / SEBI circular) + empanelled-vendor context
  → Safety/compliance disclaimer
```

## J6 — Switch language mid-conversation (cross-cutting)
```
Any widget conversation → tap EN/हिं/தமிழ்
  → UI labels + last answer re-render in chosen language
  → Citations preserved; conversation continues
```

## J7 — Escalate to human (cross-cutting)
```
Assistant can't resolve / user taps "Talk to a human"
  → Collect contact + context → handoff (ticket/lead) with full transcript
  → Confirmation + expected response time
```

## Journey → page/CTA map
| Journey | Entry page | Key CTA |
|---|---|---|
| J1 Buyer eval | Home | Book a demo |
| J2 Compliance | Capability page | View source |
| J3 Stock Q | Stock Research / widget | Try the assistant |
| J4 NALCO | NALCO Intelligence | Explain a filing |
| J5 Algo | Algo Education | Try the assistant |
| J6 Language | Any | EN/HI/TA switch |
| J7 Escalation | Any (widget) | Talk to a human |
