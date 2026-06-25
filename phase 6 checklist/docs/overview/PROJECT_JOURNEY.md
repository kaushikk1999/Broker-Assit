# Project Journey — every step, how it was done

This document walks the **entire project from idea to working software**, phase by phase. For each
phase it covers: the **goal**, the **steps taken**, **how each step was done**, the **deliverables
produced**, the **decisions locked in**, and the **outcome**.

The program deliberately follows the roadmap principle **"research before code, design before
coding."** That is why the work is staged: nothing was built until the market was understood (Phase 0)
and the experience was designed (Phase 1).

```
Phase 0 ── Research ──▶ Phase 1 ── UX Design ──▶ Phase 2 ── Architecture + Build ──▶ Phase 3 ── Backend foundation ──▶ (next) real vendors
 competitive gap        IA, personas,            mocks-first thin-slice            auth, persistence,           ingestion worker,
 analysis               journeys, wireframes     (NALCO knowledge RAG)             abuse control, infra         live AI + market data
```

---

## The vision (the "why")

Indian retail investors who prefer **Hindi or Tamil** have no trustworthy, **source-cited** assistant
that can explain **stocks, regulatory filings, and algo-trading rules** in plain language. Brokerages,
meanwhile, carry that support load through tickets and app-only chatbots.

**BrokerAssist** is the answer: a **drop-in embeddable widget** a brokerage adds to its website with
one snippet. It is **multi-tenant SaaS** — each brokerage gets a public widget key + a domain
allowlist. Every answer is **cited** and carries an **"informational only — not investment advice"**
disclaimer.

---

## Phase 0 — Research & competitive analysis  ✅

**Goal:** prove there is a real, unoccupied gap before spending a rupee on engineering.
**Folder:** [`deliverables/phase_0/`](../../deliverables/phase_0/)

### Steps & how they were done

1. **Locked the owner decisions first** (`18_owner_decision_signoff.md`). Four decisions framed all
   research: product = embeddable widget SaaS; audience = B2B brokerages (primary); research scope =
   public web + screenshots only (no logins/paid tools); pricing page deferred → 5 in-scope pages.
2. **Set a research-permissions policy** (`19_research_permissions_matrix.md`) so findings stayed
   defensible — only public sources, with anything behind a login honestly flagged "Not verified."
3. **Studied 10 competitors** — 5 Indian brokers (Zerodha, Upstox, Groww, ICICI Direct, Angel One) and
   5 AI platforms (Intercom/Fin, Drift, Freshchat, Botpress, ManyChat) — logging structured findings
   in `20_actual_competitor_findings.csv` and `competitors_final.csv`.
4. **Scored a capability matrix** (`feature_matrix_final.csv`) — every competitor rated 0–5 across
   ~15 capabilities (stock info, filing explanation, citations, multilingual finance, embeddability,
   human handoff, …) for a comparable total out of 75.
5. **Wrote the gap report** (`21_phase0_final_gap_report.md`) — synthesized the matrix into gaps,
   differentiation, and risks.
6. **Produced the handoff brief** (`22_phase0_phase1_priority_brief.md`) — turned findings into
   concrete Phase 1 priorities (which pages, journeys, CTAs to design first).

### What the research found

- **The intersection nobody occupies:** no incumbent combines (1) deep Hindi **+ Tamil** finance
  support, (2) **source-cited** answers, (3) finance-domain depth (stocks, filings, NALCO, algo), and
  (4) easy **embeddability**. Brokers score 5/5 on stock info but **zero** on filing explanation,
  citations, and Tamil. Generic AI platforms have strong multilingual + RAG but **zero finance
  knowledge** out of the box.
- **Top differentiator = the wedge:** Hindi + Tamil financial assistant (Tamil finance is effectively
  absent across all 10) — and also the **biggest execution risk** (Tamil terminology / transliteration,
  heavy reliance on Sarvam AI).
- **Compliance is mandatory, not optional:** citations + disclaimers are required for a SEBI/NSE-
  sensitive audience.

**Outcome:** a validated, defensible market wedge → green-light to design.

---

## Phase 1 — UX design  ✅

**Goal:** design the buyer-facing site **and** the assistant experience — without writing app code.
**Folder:** [`deliverables/phase_1/`](../../deliverables/phase_1/)

### Steps & how they were done

1. **Information architecture & sitemap** (`00_…`). Defined 5 in-scope pages (Home, Stock Research,
   NALCO Intelligence, Algo Education, Contact) with a reserved-but-deferred Pricing slot, plus global
   elements present on every page: header nav, **EN/HI/TA language switcher**, "Book a demo" CTA, the
   floating assistant, and a compliance footer. Core IA principle: keep **marketing** and **live demo**
   layers distinct.
2. **Personas** (`01_…`), buyer-first: PRIMARY = Product/Growth lead "Ananya", Compliance officer
   "Rahul", Support head "Meera"; SECONDARY = end-investors (Hindi/Tamil retail, NALCO shareholder,
   algo-curious trader).
3. **User journeys** (`02_…`) — 7 flows: buyer evaluation (primary funnel), compliance validation,
   three end-investor demo flows (stock / NALCO filing / algo), plus cross-cutting **language switch
   mid-conversation** and **escalate to human**.
4. **Low-fi wireframes** (`03_…`) — all 5 pages in desktop + mobile, and 3 widget states (floating,
   full-screen, mobile).
5. **Content, CTAs, behavior specs** (`23`–`27`) — per-page content deck, a CTA matrix with EN/HI/TA
   variants, the widget behavior spec (floating/full-screen/escalation), and a language-behavior matrix
   (what to **translate** vs **transliterate**, and fallback rules).
6. **Visual direction + accessibility** (`28`, `29`) — style reference board and a **WCAG 2.1 AA**
   checklist (Devanagari/Tamil fonts, line-height, contrast).
7. **Signoff gate** (`30_…`) — an explicit owner approval checklist before any code.

**Key design rules that became build invariants:** language switcher is a **first-class global
control**; **citations are shown in every language**; **one primary action per page**, all funnelling
to Contact.

**Outcome:** an approved, buildable UX with the widget behavior fully specified.

---

## Phase 2 — Architecture & the build (mocks-first)  ✅

**Goal:** turn the design into a **running, production-shaped** system — the **NALCO knowledge-RAG
thin-slice** — without needing a single vendor credential.
**Folders:** [`deliverables/phase_2/discovery/`](../../deliverables/phase_2/discovery/) (decisions) and
[`deliverables/phase_2/brokerassist/`](../../deliverables/phase_2/brokerassist/) (the application).

### Step 2a — Discovery & decisions

- **Decisions log** (`discovery/00_phase2_decisions.md`): port the Phase 1 prototype to **Next.js**;
  **monorepo** on Railway; build the **NALCO knowledge-RAG slice first** (market + worker stubbed);
  **mocks-first** behind clean interfaces.
- **Architecture Decision Records** (`discovery/02_adr_log.md`) — five accepted ADRs that are the
  spine of the codebase:
  | ADR | Decision |
  |---|---|
  | ADR-001 | Mocks-first provider interfaces (every vendor behind an ABC) |
  | ADR-002 | **Citations resolve from PostgreSQL, not the vector store** |
  | ADR-003 | SQLite for dev, PostgreSQL for prod — one model layer |
  | ADR-004 | Intent-routing fork **before** retrieval (market never touches Qdrant) |
  | ADR-005 | Abuse/cost control **before** any model call |
- **Readiness scorecard** (`discovery/03_readiness_scorecard.md`) — tracks every capability as
  ✅ done (mock) / ⚠️ needs vendor creds / ⛔ deferred.

### Step 2b — Backend pipeline (how it was built)

The backend (`apps/backend`, FastAPI) was built bottom-up so each layer is independently testable:

1. **Adapter interfaces first** (`adapters/base.py`) — abstract base classes for
   `LanguageProvider`, `EmbeddingProvider`, `VectorStore`, `ReRanker`, `LLM`, `MarketDataProvider`.
   **No model weights run in-process** — each is a remote call behind an interface.
2. **Deterministic mocks** (`adapters/mocks.py`) — a mock per interface: language detect/translate
   (Devanagari/Tamil regex + a small HI/TA→EN term map), a hash-based embedding, a **real RRF hybrid
   search** over the seeded chunks (dense token-overlap + BM25-lite sparse), a cross-encoder-proxy
   reranker, a **grounded** mock LLM (returns the top chunk verbatim — never hallucinates), and a
   hash-seeded market provider. A factory (`adapters/__init__.py`) returns mock or real by
   `BA_USE_MOCKS`.
3. **Intent router** (`services/intent_router.py`) — `classify()` forks market (keyword + known
   symbol) vs knowledge.
4. **Two branches** — `services/market_service.py` (Redis-cached quotes, never Qdrant) and
   `services/rag_pipeline.py` (the 8-stage pipeline, see [RAG_PIPELINE.md](../reference/RAG_PIPELINE.md)).
5. **Chat endpoint** wires it together (`api/routes_chat.py`): session → security gate → classify →
   branch → persist → respond.

### Step 2c — Frontend (how it was built)

The Phase 1 prototype was ported to **Next.js 14 (App Router)** (`apps/frontend`): 5 pages, an
`i18n` hook (EN/HI/TA), the `Assistant` widget (which listens for a `ba-ask` window event), an
`AskButton` that deep-links a query, and `lib/api.js` — the single network boundary that creates a
session then posts chat messages.

**Outcome:** the **whole pipeline runs credential-free** end-to-end; 8 tests passing at the close of
Phase 2.

---

## Phase 3 — Backend foundation (auth, persistence, abuse control, real infra)  ✅

**Goal:** make the pilot **safe to expose** and **ready to point at real infrastructure** — while AI
stays mocked.

### Steps & how they were done

1. **Widget security** (`core/security.py`) — public key looked up by **SHA-256 hash**, request
   **Origin matched against the tenant allowlist** (exact host[:port] or `*.` wildcard), and an
   anonymous **signed session JWT** (30-min TTL). No login for investors.
2. **Admin plane** (`core/admin_security.py`, `api/routes_admin.py`) — **bcrypt** login with
   **failed-attempt lockout**, admin JWT (1-hr), role checks (`admin` / `superadmin`), and tenant /
   API-key / allowlist / quota management — **every write audited**.
3. **Abuse & cost control** (`core/ratelimit.py`) — per-session/min, per-IP/min rate limits + a
   **per-tenant daily quota**, all enforced **before any model call**. A **Redis hot counter** does
   enforcement; **PostgreSQL** is the durable backstop. Breaches are logged to `abuse_events`.
4. **Normalized persistence** (`db/models.py`, `db/seed.py`) — 16 tables: tenancy, document registry
   (+ versions + audit), chat history, quotas, analytics, feedback, abuse + admin audit. **Alembic**
   migrations (`alembic/versions/0001_initial.py`); idempotent `seed()` for dev.
5. **Real infra wiring** — `docker-compose.yml` (Postgres + Redis + Qdrant + backend); `core/redis.py`
   (real Redis when `BA_REDIS_URL` set, in-memory fallback otherwise); `adapters/qdrant_real.py`
   (startup **collection validation** — asserts dense + native sparse and an **FK-only payload
   contract** — no ingestion yet).
6. **Observability** (`core/observability.py`) — JSON structured logging + an **X-Request-ID**
   correlation middleware; `/health`, `/ready` (per-dependency), `/live`.

**Outcome:** auth/access control, persistence, abuse control, module APIs, and real-infra wiring all
landed. **20 tests passing.** Verified end-to-end (see [TESTING.md](../reference/TESTING.md)).

---

## How a single question flows today (end-to-end recap)

1. Brokerage page loads the widget → it calls `POST /session` with the widget key + Origin.
2. Backend verifies key hash + allowlist → returns a 30-min session JWT.
3. Investor asks a question → `POST /chat` with the Bearer token.
4. **Security gate** (rate limits + quota) runs **before any model call**.
5. **Intent router** forks: market → cached quote; knowledge → the 8-stage RAG pipeline.
6. Answer + **citations (from PostgreSQL)** + disclaimer returned and rendered in the widget, in the
   user's language.

See [ARCHITECTURE.md](ARCHITECTURE.md) and the [diagrams](../diagrams/) for the visual version.

---

## What's next (deferred workstreams)

Gated on **vendor accounts/credentials and discovery inputs — not on more design** (per the readiness
scorecard verdict):

- Wire **real adapters** (`BA_USE_MOCKS=false`): Sarvam, Ollama Cloud (embeddinggemma + Gemma), a
  hosted re-ranker, and TrueData market data.
- Build the **ingestion / embedding worker** (chunk → embed → upsert into Qdrant).
- Settle the open ADRs: Qdrant hosting, re-ranker provider, market-data licensing, source-authority
  precedence, Railway secrets.
- Hi-fi visual design + brand confirmation.

Full implemented-vs-deferred detail: [STATUS.md](../planning/PHASE_STATUS.md).
