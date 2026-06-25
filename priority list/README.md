# 📋 Priority List — Upload Order Guide

**Total files organized: 150**
All files copied from the AI bot project, organized by upload priority.

---

## 📁 Folder Structure

### 🔴 Priority 1 — Must Upload First (Project Understanding)
```
priority_1_must_upload_first/
├── root_file_tree/          → file_tree.txt (complete project tree)
├── dependency_files/        → requirements.txt, package.json, package-lock.json
├── environment_config/      → .env.example, config.py, docker-compose.yml, alembic.ini,
│                              next.config.mjs, railway.md, .gitignore files
└── project_docs/
    ├── root/                → README.md, CLAUDE.md (root + docs + deliverables + brokerassist)
    ├── docs_overview/       → ARCHITECTURE.md, PROJECT_JOURNEY.md, PROJECT_STRUCTURE.md
    ├── docs_planning/       → ROADMAP.md, PHASE_STATUS.md, NEXT_PHASE_PLAN.md,
    │                          PHASE_4_PLAN.md, PHASE_5_KICKOFF.md, HANDOFF_TO_PHASE_5.md,
    │                          DECISIONS_AND_OPEN_ITEMS.md
    ├── docs_reference/      → API_REFERENCE.md, DATA_MODEL.md, RAG_PIPELINE.md,
    │                          SECURITY.md, SETUP_AND_RUN.md, TESTING.md
    └── docs_diagrams/       → system-architecture, data-model, rag-pipeline,
                               request-lifecycle, roadmap-status (.png + .svg)
```

### 🟠 Priority 2 — Backend Core (Data Flow & Implementation)
```
priority_2_backend_core/
├── entrypoint/              → main.py, app __init__.py
├── routes/                  → routes_admin.py, routes_chat.py, routes_meta.py, routes_modules.py
├── services/                → admin_service.py, intent_router.py, market_service.py,
│                              persistence.py, rag_pipeline.py
├── schemas/                 → admin.py, chat.py, modules.py
├── core/                    → security.py, admin_security.py, ratelimit.py,
│                              observability.py, redis.py
├── database/                → models.py, base.py, seed.py
├── migrations/              → alembic env.py, 0001_initial.py, script.py.mako
├── tests/                   → conftest.py, test_phase3.py, test_pipeline.py
└── Dockerfile
```

### 🟡 Priority 3 — Feature-Specific Core (RAG / AI)
```
priority_3_feature_core/
├── ai_adapters/             → adapters __init__.py, base.py (interfaces),
│                              mocks.py (mock implementations), qdrant_real.py
├── rag_pipeline/            → rag_pipeline.py, intent_router.py, RAG_PIPELINE_docs.md
└── discovery/               → phase2_decisions.md, information_inventory.md,
                               adr_log.md, readiness_scorecard.md
```

### 🟢 Priority 4 — Frontend (Product Completeness)
```
priority_4_frontend/
├── pages/                   → page.jsx, layout.jsx, template.jsx, globals.css,
│                              algo-education, contact, nalco, stock-research pages
├── components/              → AskButton.jsx, Assistant.jsx (chat widget), Header.jsx
├── lib/                     → api.js, i18n.js
├── config/                  → package.json, next.config.mjs, .env.local.example
└── phase1_prototype/        → HTML prototype (index, algo-education, contact, nalco,
                               stock-research, server.js, app.js, styles.css)
```

### 🔵 Priority 5 — Deployment / Infra / Ops
```
priority_5_deployment_infra/
├── deployment/              → Dockerfile, docker-compose.yml, railway.md
├── security_monitoring/     → security.py, admin_security.py, ratelimit.py,
│                              observability.py, redis.py, SECURITY_docs.md,
│                              SETUP_AND_RUN_docs.md, TESTING_docs.md
├── earlier_phase_deliverables/
│   ├── phase_0/             → research, gap reports, competitor analysis, signoff
│   └── phase_1/             → personas, user journeys, wireframes, content deck,
│                              widget spec, accessibility checklist, signoff
└── data/                    → CSV files (competitors, feature matrix — filled + raw)
```

---

## ⚡ Fastest Upload Order (Minimum Set First)

| Order | What to Upload | Folder |
|-------|---------------|--------|
| 1 | Root file tree | `priority_1.../root_file_tree/` |
| 2 | All READMEs + roadmap + phase docs | `priority_1.../project_docs/` |
| 3 | requirements.txt + package.json | `priority_1.../dependency_files/` |
| 4 | Backend entrypoint (main.py) | `priority_2.../entrypoint/` |
| 5 | Backend folder (routes → services → schemas → core) | `priority_2.../` |
| 6 | Database models + migrations | `priority_2.../database/` + `migrations/` |
| 7 | RAG / AI adapters / Qdrant | `priority_3.../` |
| 8 | Deployment files | `priority_5.../deployment/` |
| 9 | Frontend folder | `priority_4.../` |

---

## 📝 Notes
- Files are **copies** (originals remain in place)
- `.next/`, `node_modules/`, `__pycache__/`, `.git/` excluded
- `.xlsx`, `.pdf`, `.docx` reference files NOT copied (too large / binary)
- Archives (`.zip`) NOT copied
