# Phase 1 — Widget Behavior Spec

_Behavioral spec for the embeddable assistant in its three experiences. Visual design follows signoff._

## Floating widget
- **Launcher:** bottom-right bubble `(•)` on every page; 56px touch target; subtle pulse on first load.
- **Open:** docked panel ~380px wide, ~600px tall (desktop); does not block page scroll.
- **Header:** title · language switcher (EN/हिं/தமிழ்) · expand-to-fullscreen · close.
- **Greeting:** suggests the 3 capabilities (stocks / filings / algo) in the active language.
- **Message:** user bubble + bot bubble; bot answers carry **citation chips** ("source ↗") that open the
  source doc. Streaming/typing indicator while generating.
- **Persistence:** conversation + chosen language persist across page navigation within a session.
- **Entry seeding:** "Try the assistant" buttons open the widget pre-filled with a page-relevant prompt.

## Full-screen assistant
- **Trigger:** expand icon in the docked header, or dedicated "full-screen" CTA.
- **Layout:** two-pane — left: suggested prompts + **Sources/citations panel**; right: conversation.
- **Use:** longer research sessions; same engine, more room for citations and follow-ups.
- **Exit:** collapses back to docked widget, conversation preserved.

## Mobile behavior
- **Launcher:** same bottom-right; opens a **full-bleed sheet** (not a small docked panel).
- **Input:** sticky bottom input + send, thumb-reachable; respects keyboard insets (safe-area).
- **Language switch:** top of sheet; one tap.
- **Single-pane:** citations inline under each answer (no side panel on small screens).

## Escalation behavior (human handoff)
- **Triggers:** user taps "Talk to a human"; or assistant low-confidence / repeated no-answer.
- **Flow:** collect contact + reason → package full transcript + detected language → create lead/ticket
  → confirm with expected response time.
- **Compliance:** every answer carries a disclaimer (informational, not investment advice); algo/finance
  answers always cite source; never fabricate a citation.

## States to design (for hi-fi)
Idle/launcher · greeting · typing · answer-with-citation · language-switch · escalation form ·
error/no-answer · offline/loading.
