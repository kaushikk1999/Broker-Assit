# Phase 1 — Accessibility QA Checklist

_Target: **WCAG 2.1 AA**. Applies to site + embedded widget, across EN/HI/TA._

## Perceivable
- [ ] Text contrast ≥ 4.5:1 (≥ 3:1 for large text & UI components).
- [ ] No information conveyed by color alone (citations/disclaimers also use icon + label).
- [ ] Indic scripts (Devanagari, Tamil) render with adequate size & line-height; no clipping/truncation.
- [ ] Images have alt text; product screenshots described.

## Operable
- [ ] Full keyboard navigation (site + widget): open widget, type, send, switch language, escalate, close.
- [ ] Visible focus indicators on all interactive elements.
- [ ] Touch targets ≥ 44×44px (mobile widget, CTAs, language switcher).
- [ ] No keyboard traps in the full-screen assistant; ESC closes overlays.

## Understandable
- [ ] `lang` attribute set correctly per content (`en`, `hi`, `ta`) and updated on language switch.
- [ ] Plain-language answers; finance jargon glossed.
- [ ] Form fields labeled; errors described in text + programmatically associated.
- [ ] Disclaimers present and legible on every assistant answer.

## Robust
- [ ] Semantic HTML / ARIA roles for chat (log/status), buttons, dialogs.
- [ ] Screen-reader announces new assistant messages (aria-live) and citations.
- [ ] Widget works embedded in a third-party page without breaking host a11y.
- [ ] Respects reduced-motion and user font-size/zoom (up to 200%).

## Multilingual-specific
- [ ] Language switch announced to assistive tech; conversation continues.
- [ ] Citations remain accessible and openable in every language.
- [ ] RTL not required (EN/HI/TA are LTR) — confirm no accidental RTL styling.

## Sign-off
- [ ] Automated scan (axe/Lighthouse) passes; [ ] manual keyboard pass; [ ] screen-reader pass (NVDA/VoiceOver).
