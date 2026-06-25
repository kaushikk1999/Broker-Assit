# Testing & Verification

How to test BrokerAssist, plus the **full-depth verification report** from the last end-to-end run
(2026-06-24, mocks-first dev mode).

---

## 1. Automated tests (pytest)

```bash
cd deliverables/phase_2/brokerassist/apps/backend
source .venv/bin/activate
pytest -q
```

**Result: 20 passed.** Suites:

| File | Covers |
|---|---|
| `tests/test_pipeline.py` | Intent routing (market vs knowledge), the RAG branch, multilingual translation, the citations-from-Postgres invariant, the relevance gate |
| `tests/test_phase3.py` | Widget auth (key + Origin), session JWT, rate limits, daily quota, the admin plane (login/lockout/roles/audit) |
| `tests/conftest.py` | Fresh SQLite + mock-AI fixture per test |

Tests use `create_all()` on a throwaway database and the deterministic mocks, so they need **no
external services**.

---

## 2. Frontend build check

```bash
cd deliverables/phase_2/brokerassist/apps/frontend
npm run build
```
The Next.js production build type-checks and **static-generates all 8 routes** (`/`, `/stock-research`,
`/nalco`, `/algo-education`, `/contact`, plus `_not-found`) — the strongest correctness signal for the
frontend.

---

## 3. Manual end-to-end checklist

With the backend on `:8200` and frontend on `:3000`:

1. `GET /health` → `200`.
2. `POST /session` (Origin `http://localhost:3000`) → session token.
3. `POST /chat` "Explain NALCO latest quarterly result" → cited knowledge answer.
4. `POST /chat` "What is the LTP of NALCO?" → market quote, no citations.
5. `POST /chat` "hello there" → friendly fallback, no citations.
6. Bad Origin / bad key / no token → `403` / `401` / `401`.
7. Admin login → `/admin/tenants` lists tenants.
8. Open `http://localhost:3000`, click **"Try the assistant"**, switch to हिं → widget answers with
   citations and the UI localizes.

---

## 4. Full-depth verification report (2026-06-24)

Every layer was exercised against the live mock stack. **All checks passed; no errors found, nothing
required fixing.**

### Backend

| Check | Result |
|---|---|
| `pytest` suite | ✅ **20/20 passed** (1.9 s) |
| Server boot | ✅ Clean; Qdrant validation correctly `skipped` (no `BA_QDRANT_URL` in dev) |
| `/`, `/health`, `/live`, `/ready` | ✅ `/ready` → postgres ok, redis `memory` ok, 2 tenants, 4 docs |
| `POST /session` (key + Origin) | ✅ 30-min session JWT issued |
| `/chat` — knowledge | ✅ Grounded answer + **3 citations** + disclaimer, `branch:knowledge` |
| `/chat` — market | ✅ `branch:market`, LTP quote, `citations:[]` |
| `/chat` — Hindi | ✅ Routed, `intent:filing_dividend`, `language:hi` |
| `/chat` — off-topic | ✅ Relevance gate → fallback, **no fabricated citations**, `grounded:false` |
| `/search`, `/filings`, `/stock` | ✅ All return correct envelopes |
| Security — bad Origin | ✅ **403** `Origin 'evil.com' not allowlisted` |
| Security — bad key / no token / wrong admin pw | ✅ **401** each |
| Admin `/login` + `/tenants` | ✅ bcrypt login; tenant list returned |
| Rate limiting (25 rapid `/chat`) | ✅ Exactly **20 × 200 then 5 × 429** |

### Frontend

| Check | Result |
|---|---|
| `next build` | ✅ All **8 pages** compile + type-check + static-generate |
| Homepage render | ✅ Nav, hero, cards, stats, footer, launcher |
| Console errors | ✅ **None** |
| **Widget → backend (E2E)** | ✅ "Try the assistant" → live RAG answer with `knowledge` badge, **3 clickable citations**, disclaimer |
| Language toggle EN → हिं | ✅ Entire UI + widget localizes (nav, hero, widget title, citation labels, escalation link) |

### Known, by-design behaviour (not a bug)

In mocks-first mode the AI providers are stubs, so a Hindi **chat answer's body text** comes back in
English while routing, language tracking, citations, and **all frontend UI strings** are fully
localized. Real translation/generation activates when `BA_USE_MOCKS=false` and the Sarvam/Gemma
adapters are wired (see [SETUP_AND_RUN.md](SETUP_AND_RUN.md#6-promote-to-real-vendors-next-workstream)).

---

## 5. Reproduce the verification quickly

```bash
# backend up
cd deliverables/phase_2/brokerassist/apps/backend && source .venv/bin/activate
uvicorn app.main:app --port 8200 &

# one-shot E2E
B=http://localhost:8200
TOKEN=$(curl -s -X POST $B/api/v1/session -H "Origin: http://localhost:3000" \
  -H "Content-Type: application/json" -d '{"widget_key":"demo-public-key"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['session_token'])")
curl -s -X POST $B/api/v1/chat -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"message":"Explain NALCO latest quarterly result"}'
```
