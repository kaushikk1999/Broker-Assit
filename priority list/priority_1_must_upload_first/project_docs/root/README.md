# BrokerAssist

> Multilingual · cited · embeddable AI assistant for stock brokerages.
> NALCO knowledge pilot — mocks-first Phase 2 / 3.

A B2B SaaS widget a brokerage embeds on its website: an AI assistant that answers investor questions
about stocks, regulatory filings, and algo-trading education — in **English, Hindi, or Tamil**, always
**with citations** and an *"informational only — not investment advice"* disclaimer.

## 📖 Start with the docs

The [`docs/`](docs/) folder is the full engineering documentation, arranged into `planning/`,
`overview/`, `reference/`, and `diagrams/`. Best entry points:

- **AI agent / picking this up?** → **[docs/CLAUDE.md](docs/CLAUDE.md)** then **[docs/planning/PHASE_STATUS.md](docs/planning/PHASE_STATUS.md)**.
- **Plan the next phase** → **[docs/planning/NEXT_PHASE_PLAN.md](docs/planning/NEXT_PHASE_PLAN.md)** · **[docs/planning/ROADMAP.md](docs/planning/ROADMAP.md)**
- **Understand it** → **[docs/overview/PROJECT_JOURNEY.md](docs/overview/PROJECT_JOURNEY.md)** · **[docs/overview/ARCHITECTURE.md](docs/overview/ARCHITECTURE.md)**
- **Build/operate it** → **[docs/reference/SETUP_AND_RUN.md](docs/reference/SETUP_AND_RUN.md)** · **[API](docs/reference/API_REFERENCE.md)** · **[Data model](docs/reference/DATA_MODEL.md)** · **[RAG](docs/reference/RAG_PIPELINE.md)** · **[Security](docs/reference/SECURITY.md)** · **[Testing](docs/reference/TESTING.md)**
- **Full index** → **[docs/README.md](docs/README.md)**

## 🗂️ Repository map

| Folder | Contents |
|---|---|
| [`docs/`](docs/) | Documentation + architecture diagrams |
| [`deliverables/`](deliverables/) | Phased work products — **the application is in [`phase_2/brokerassist/`](deliverables/phase_2/brokerassist/)** |
| [`reference/`](reference/) | Source material — roadmap, FAQ, vendor lists (PDF/DOCX) |
| [`data/`](data/) | Research datasets (`raw/` inputs, `filled/` processed) |
| [`archives/`](archives/) | Zipped snapshots of earlier phases |

## 🚀 Run it (no credentials needed)

```bash
cd deliverables/phase_2/brokerassist/apps/backend
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8200      # http://localhost:8200/docs  ·  pytest -q → 20 passing
```

Frontend: `cd deliverables/phase_2/brokerassist/apps/frontend && npm install && npm run dev`.

The whole pipeline runs **mocks-first** (`BA_USE_MOCKS=true`): SQLite + in-memory Redis + mock AI, so
there are no external dependencies for local development. See
[docs/reference/SETUP_AND_RUN.md](docs/reference/SETUP_AND_RUN.md) for the full quick-start.

## At a glance

![System architecture](docs/diagrams/system-architecture.svg)
