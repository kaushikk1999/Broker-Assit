# BrokerAssist — Phase 1.5 static prototype

A real, runnable front-end of the Phase 1 design. **No backend, no build step, mock data.**
Plain HTML/CSS/JS. Demonstrates the 5-page B2B marketing/demo site, the embedded multilingual
assistant, and citation-backed mock answers in **English / Hindi / Tamil**.

## Run it

Any static file server works. From this `prototype/` folder:

```bash
# Option A — Python (no install)
python3 -m http.server 8123

# Option B — Node
npx serve -l 8123        # or: npx http-server -p 8123
```

Then open <http://localhost:8123/> in a browser.

> Open via the server URL, not by double-clicking the file — the shared header/footer/widget are
> injected by JavaScript and language/state work best over `http://`.

## What to try
- **Language switcher** (top-right, also inside the widget): EN / हिं / தமிழ். Choice persists across pages.
- **Chat launcher** (bottom-right): ask about a *stock*, a *NALCO* filing, or *white-box vs black-box
  algos* — each mock answer comes back with a **source citation** and a disclaimer. Full-screen toggle included.
- **Capability pages** (Stock Research, NALCO, Algo): in-page demo + "Try the assistant" buttons that
  push the question into the widget.
- **Contact**: the primary B2B conversion form (submits to a local success message — nothing is sent).

## Files
```
index.html            Home
stock-research.html   Stock Research (capability demo)
nalco.html            NALCO Intelligence (capability demo)
algo-education.html   Algo Education (capability demo)
contact.html          Contact / Book a demo
assets/styles.css     Design system (light + dark mode)
assets/app.js         i18n dictionary, shared chrome, mock assistant
```

## Scope & caveats
- Front-end only. Assistant replies are **canned mock content**; no LLM/RAG/market data.
- Pricing page is **deferred** (nav shows a "Soon" badge), per the Phase 1 decision.
- NALCO answers use **illustrative data** until real investor-relations sources are connected.
- Fonts (Noto Sans / Devanagari / Tamil) and the Tabler icon set load from CDN; with no network the
  site still works using system-font fallbacks (icons may not render).
- This is a throwaway Phase-1.5 artifact to validate UX — not the Phase 2+ production Next.js app.
