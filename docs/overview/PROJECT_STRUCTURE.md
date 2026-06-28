# Project Structure

This repository holds the **BrokerAssist** program: phased research/design deliverables plus the
runnable Phase 2/3 application. It was reorganized on 2026-06-24 so that loose source files at the
root are sorted into clear, purpose-named folders.

## Top-level layout

```
AI bot/
├── README.md                  Project entry point & navigation
├── CLAUDE.md                  Auto-loaded agent context (status + invariants)
├── .gitignore                 Ignores deps, build caches, secrets, OS junk
│
├── docs/                      📖 Documentation (this folder)
│   ├── README.md              Docs index (this map)
│   ├── CLAUDE.md              🤖 Agent entry point (orientation + working agreement)
│   ├── planning/             🧭 Status & what's next (plan the next phase here)
│   │   ├── PHASE_STATUS.md     Current state of every phase & capability — source of truth
│   │   ├── NEXT_PHASE_PLAN.md  Executable plans for upcoming workstreams
│   │   ├── DECISIONS_AND_OPEN_ITEMS.md  Settled decisions + open ADRs/inputs
│   │   ├── ROADMAP.md          Visual phase roadmap with status
│   │   ├── PHASE_4_PLAN.md     Phase 4 (Data Ingestion) implementation plan
│   │   ├── PHASE_5_KICKOFF.md  Phase 5 (Embedding) kickoff brief (implemented)
│   │   ├── PHASE_6_KICKOFF.md  Phase 6 (RAG System) kickoff brief
│   │   ├── HANDOFF_TO_PHASE_5.md Phase 5 handoff guide
│   │   └── HANDOFF_TO_PHASE_6.md Phase 6 handoff guide (latest)
│   ├── overview/             📖 Understand the project
│   │   ├── PROJECT_JOURNEY.md  Whole project step-by-step (phases 0→3)
│   │   ├── ARCHITECTURE.md     Full architecture reference (with diagrams)
│   │   └── PROJECT_STRUCTURE.md  This file
│   ├── reference/            🔧 Build & operate
│   │   ├── SETUP_AND_RUN.md    Run locally, config reference, deploy
│   │   ├── API_REFERENCE.md    Every endpoint + curl examples
│   │   ├── DATA_MODEL.md       All 16 tables + ER diagram
│   │   ├── RAG_PIPELINE.md     The 8-stage knowledge pipeline deep dive
│   │   ├── SECURITY.md         Auth planes, abuse control, admin plane
│   │   └── TESTING.md          Test guide + full verification report
│   └── diagrams/              Architecture images (SVG source + PNG raster)
│       ├── roadmap-status.svg / .png
│       ├── system-architecture.svg / .png
│       ├── rag-pipeline.svg / .png
│       ├── request-lifecycle.svg / .png
│       └── data-model.svg / .png
│
├── deliverables/              📦 Phased work products (the program of record)
│   ├── README.md              Phase 0 & 1 deliverables index
│   ├── phase_0/               Research & competitive analysis
│   ├── phase_1/               UX design (IA, personas, journeys, wireframes, prototype)
│   └── phase_2/               Architecture + the application
│       ├── discovery/         Decisions log, ADRs, readiness scorecard
│       └── brokerassist/      ⭐ THE APPLICATION (FastAPI + Next.js monorepo)
│
├── reference/                 📚 Source material (read-only inputs)
│   ├── AI_Brokerage_Assistant_Roadmap_Merged.docx
│   ├── Production-Ready AI Brokerage Assistant.pdf
│   ├── FAQ_Retail_Algo_03112025_NSE.pdf
│   └── List of Authoized Vendors_2.pdf
│
├── data/                      📊 Datasets
│   ├── raw/                   Original research inputs (competitors, feature matrix, vendor lists)
│   └── filled/                Processed / filled CSVs
│
└── archives/                  🗄️ Zipped snapshots of earlier phases
    ├── phase 0 and 1.zip
    └── phase2_hybrid_best_of_both.zip
```

## The application — `deliverables/phase_2/brokerassist/`

```
brokerassist/
├── README.md                  How to run backend, frontend, and Phase 3 infra
├── docker-compose.yml         Local Postgres + Redis + Qdrant + backend
├── infra/railway.md           Railway deployment topology notes
│
├── apps/
│   ├── backend/               FastAPI service
│   │   ├── app/
│   │   │   ├── main.py        App factory, lifespan (seed + Qdrant validate), routers
│   │   │   ├── config.py      Central BA_-prefixed settings (mocks-first switch)
│   │   │   ├── api/           routes_chat · routes_modules · routes_admin · routes_meta
│   │   │   ├── services/      intent_router · market_service · rag_pipeline · persistence · admin
│   │   │   ├── core/          security · admin_security · ratelimit · redis · observability
│   │   │   ├── adapters/      base (interfaces) · mocks · qdrant_real (factory in __init__)
│   │   │   ├── db/            models · base · seed
│   │   │   └── schemas/       Pydantic request/response models
│   │   ├── alembic/           Migrations (0001_initial)
│   │   ├── tests/             test_pipeline.py · test_phase3.py (20 passing)
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── frontend/              Next.js 14 (App Router)
│       ├── app/               Pages: home · stock-research · algo-education · nalco · contact
│       ├── components/        Assistant · AskButton · Header
│       ├── lib/               api.js (network boundary) · i18n.js (EN/HI/TA)
│       └── package.json
│
└── packages/
    └── widget/               (placeholder) standalone embeddable widget build target
```

## What moved during the 2026-06-24 reorganization

| Before (loose at root) | After |
|---|---|
| `*.pdf`, `*.docx` (roadmap, FAQ, vendor list) | `reference/` |
| `competitors.csv`, `feature_matrix.csv`, `*.xlsx` | `data/raw/` |
| `files/*_filled.csv` | `data/filled/` |
| `phase 0 and 1.zip`, `phase2_hybrid_best_of_both.zip` | `archives/` |
| `.DS_Store` (×N) | deleted (OS junk) |
| `__pycache__/`, `.pytest_cache/`, `.next/` | deleted (regenerated build caches) |
| — | `docs/` created (this documentation) |

> Notes
> - The `deliverables/` tree was **not** restructured — it is an intentional, already-organized
>   record of the phased delivery, and its internal READMEs reference these paths.
> - Application dependencies (`node_modules/`, `.venv/`) were **kept in place** so the app remains
>   immediately runnable; they are git-ignored rather than deleted.
