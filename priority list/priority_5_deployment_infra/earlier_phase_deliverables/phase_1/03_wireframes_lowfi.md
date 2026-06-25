# Phase 1 — Low-Fidelity Wireframes

_Text/ASCII wireframes. Each page shown desktop + mobile. Hi-fi/visual mockups follow after signoff._
_Legend: `[ ]` button · `(•)` widget launcher · `〔 〕` input · `“src”` citation chip._

---
## Global header (all pages)
```
DESKTOP: [Logo]  Home  Stock Research  NALCO  Algo Education  Contact     [EN|हिं|தமிழ்]  [ Book a demo ]
MOBILE : [Logo] ───────────────────────────────────────────────────────  [☰]  [EN|हिं|தமிழ்]
```

---
## 1. HOME
```
DESKTOP                                                   MOBILE
┌──────────────── HEADER ────────────────┐                ┌─ HEADER ─┐
│ HERO                                    │                │  HERO    │
│  H1: Multilingual, cited AI assistant   │                │  H1      │
│      for brokerages (EN · हिं · தமிழ்)   │                │  Subhead │
│  Sub: Deflect tickets. Explain filings. │                │ [Book demo]
│  [ Book a demo ] [ Try the assistant ]  │   (•)          │ [Try it] │
├─────────────────────────────────────────┤                ├──────────┤
│ 4 DIFFERENTIATOR CARDS                   │                │ Diff 1   │
│ [Hindi+Tamil] [Citations] [Finance depth]│                │ Diff 2   │
│ [Drop-in embed]                          │                │ Diff 3   │
├─────────────────────────────────────────┤                │ Diff 4   │
│ LIVE DEMO PANEL                          │                ├──────────┤
│  〔 Ask: "Explain NALCO's latest result”〕│                │ LIVE DEMO│
│  → cited answer  “NSE filing ↗”          │                │  panel   │
├─────────────────────────────────────────┤                ├──────────┤
│ HOW IT WORKS (embed snippet) · LOGOS     │                │ How/embed│
│ CTA BAND: [ Book a demo ]                │                │ [Book]   │
│ FOOTER + disclaimer + lang switch        │                │ Footer   │
└──────────────────────────────────── (•) ┘                └──── (•) ─┘
```

## 2. STOCK RESEARCH  (capability demo)
```
DESKTOP                                                   MOBILE
┌ HEADER ─────────────────────────────────┐               ┌ HEADER ┐
│ H1: Stock information your investors     │               │ H1      │
│     can actually understand              │               │ Intro   │
│ Intro + "This is the live assistant"     │               ├─────────┤
├──────────────┬──────────────────────────┤               │ DEMO    │
│ DEMO CHAT     │ SAMPLE PROMPTS           │               │ chat    │
│ 〔ask a stock〕│ • Latest result?         │               │ 〔ask〕  │
│ answer +      │ • P/E vs peers?          │               │ prompts │
│ “source ↗”    │ • [EN|हिं|தமிழ்]          │               ├─────────┤
├──────────────┴──────────────────────────┤               │ Capab.  │
│ CAPABILITY BULLETS · CTA [Book a demo]   │               │ [Book]  │
│ FOOTER                                   │               │ Footer  │
└──────────────────────────────────── (•) ┘               └── (•) ──┘
```

## 3. NALCO INTELLIGENCE  (capability demo)
```
DESKTOP                                                   MOBILE
┌ HEADER ─────────────────────────────────┐               ┌ HEADER ┐
│ H1: Turn dense filings into plain answers│               │ H1     │
│ DEMO: 〔“Explain NALCO's latest filing”〕 │               │ DEMO   │
│  → summary + key figures                 │               │ chat   │
│  → “NALCO disclosure ↗” citation         │               │ cites  │
│  → [Explain in Tamil]                    │               ├────────┤
│ (note: sample data until sources final)  │               │ note   │
│ CAPABILITY · CTA [Book a demo] · FOOTER  │               │ [Book] │
└──────────────────────────────────── (•) ┘               └─ (•) ──┘
```

## 4. ALGO EDUCATION  (capability demo)
```
DESKTOP                                                   MOBILE
┌ HEADER ─────────────────────────────────┐               ┌ HEADER ┐
│ H1: Safe, regulation-cited algo learning │               │ H1     │
│ DEMO: 〔“White-box vs black-box algos?”〕 │               │ DEMO   │
│  → cited answer  “NSE FAQ ↗ / SEBI ↗”    │               │ cites  │
│  → empanelled-vendor context             │               │ disclm │
│  → ⚠ compliance disclaimer               │               ├────────┤
│ TOPICS GRID · CTA [Book a demo] · FOOTER │               │ [Book] │
└──────────────────────────────────── (•) ┘               └─ (•) ──┘
```

## 5. CONTACT  (PRIMARY conversion)
```
DESKTOP                                                   MOBILE
┌ HEADER ─────────────────────────────────┐               ┌ HEADER ┐
│ H1: Book a demo / Request access         │               │ H1     │
├──────────────┬──────────────────────────┤               │ Form:  │
│ FORM          │ WHAT YOU GET            │               │ Name   │
│ Name          │ • API key + domain      │               │ Email  │
│ Work email    │   allowlist             │               │ Broker │
│ Brokerage     │ • EN/HI/TA out of box   │               │ Size   │
│ Size (▼)      │ • Citations + handoff   │               │ Lang ☑ │
│ Languages ☑   │                         │               │ Use    │
│ Use-case      │ Direct contact / phone  │               │ [Submit│
│ [ Submit ]    │                         │               │  →demo]│
├──────────────┴──────────────────────────┤               ├────────┤
│ CONFIRMATION STATE · FOOTER              │               │ Footer │
└──────────────────────────────────── (•) ┘               └─ (•) ──┘
```

---
## Chatbot states

### A) Floating widget (collapsed → open)
```
COLLAPSED                 OPEN (docked, ~380px)
        ┌──────────────┐  ┌───────────────────────────┐
        │              │  │ Assistant     [EN|हिं|தமிழ்] ✕│
        │   page       │  ├───────────────────────────┤
        │              │  │ ⟨bot⟩ Hi! Ask about stocks,│
        │              │  │       filings, or algos.   │
        │         (•)──┼─▶│ ⟨user⟩ ...                 │
        └──────────────┘  │ ⟨bot⟩ answer  “source ↗”   │
                          │ [Talk to a human]          │
                          │ 〔 type a message…       ➤〕│
                          └───────────────────────────┘
```

### B) Full-screen assistant (expand)
```
┌───────────────────────────────────────────────┐
│ Assistant              [EN|हिं|தமிழ்]  [⤢ exit] │
├──────────────┬────────────────────────────────┤
│ Suggested     │ ⟨bot⟩ ...                       │
│ • Stock Q     │ ⟨user⟩ ...                      │
│ • Filing Q    │ ⟨bot⟩ answer                    │
│ • Algo Q      │   “NSE filing ↗”  “SEBI ↗”      │
│ Sources panel │ [Talk to a human]               │
│ (citations)   │ 〔 type…                     ➤〕 │
└──────────────┴────────────────────────────────┘
```

### C) Mobile assistant (full-bleed sheet)
```
┌──────────────┐
│ Assistant  ✕ │  [EN|हिं|தமிழ்]
├──────────────┤
│ ⟨bot⟩ ...     │
│ ⟨user⟩ ...    │
│ ⟨bot⟩ answer  │
│   “source ↗” │
│ [human]       │
├──────────────┤
│〔 type…   ➤ 〕│
└──────────────┘
(launcher → opens full-bleed; thumb-reachable input + send)
```
