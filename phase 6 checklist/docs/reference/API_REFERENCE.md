# API Reference

Complete catalogue of the BrokerAssist backend (FastAPI). Base URL in dev: `http://localhost:8200`.
Interactive docs (auto-generated from the Pydantic schemas) live at **`/docs`**.

There are **three auth planes**:

| Plane | How to authenticate | Used by |
|---|---|---|
| **Public meta** | none | health checks, transparency |
| **Widget session** | `Authorization: Bearer <session_token>` (from `/session`) | the embedded widget / investors |
| **Admin** | `Authorization: Bearer <admin_token>` (from `/admin/login`) | brokerage operators |

All examples assume `B=http://localhost:8200`.

---

## Meta & health (no auth)

### `GET /`
Service banner + endpoint list. → `{ "service", "version", "docs", "endpoints": [...] }`

### `GET /health`
Liveness + mode. → `{ "status": "ok", "use_mocks": true, "env": "local" }`

### `GET /live`
Process liveness only (no dependency checks). → `{ "status": "alive" }`

### `GET /ready`
Readiness with per-dependency status.
```json
{ "status": "ready", "tenants": 2, "documents": 4,
  "dependencies": { "postgres": {"ok": true},
                    "redis": {"backend": "memory", "ok": true},
                    "qdrant": {"configured": false} } }
```

### `GET /api/v1/admin/documents`
Transparency listing of the document registry (id, source, title, url, filing_type, filing_date).

---

## Widget session plane

### `POST /api/v1/session`
Exchange a widget key (+ allowlisted `Origin`) for a short-lived session JWT.

**Headers:** `Origin: <embedding-page-origin>` · **Body:** `{ "widget_key": "demo-public-key" }`

```bash
curl -s -X POST $B/api/v1/session -H "Origin: http://localhost:3000" \
  -H "Content-Type: application/json" -d '{"widget_key":"demo-public-key"}'
```
**200** → `{ "session_token": "<JWT>", "expires_in": 1800 }`
**Errors:** `401 Invalid widget key` / `401 Tenant inactive` / `403 Origin '…' not allowlisted`

### `POST /api/v1/chat`
The main assistant endpoint — intent-routed (market vs knowledge). Requires a session Bearer token.

**Body**
| Field | Type | Notes |
|---|---|---|
| `message` | string (1–2000) | required |
| `language` | `en` \| `hi` \| `ta` | optional; auto-detected if omitted |

```bash
curl -s -X POST $B/api/v1/chat -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"message":"Explain NALCO latest quarterly result"}'
```
**200 (knowledge branch)**
```json
{ "answer": "NALCO reported higher revenue this quarter...",
  "language": "en", "intent": "knowledge_general", "branch": "knowledge",
  "citations": [
    {"document_id":1,"chunk_id":1,"source":"NALCO_IR",
     "title":"NALCO Q4 FY25 Financial Results","url":"https://nalcoindia.com/investor/results",
     "filing_date":"2025-05-15"}
  ],
  "disclaimer": "Informational only — not investment advice.",
  "debug": {"query_en":"...","retrieved":4,"reranked":4} }
```
**200 (market branch)** — `branch:"market"`, `intent:"market_data"`, `citations:[]`, and
`debug.data` carries the quote (`symbol`, `ltp`, `currency`, `source`).

**Behaviours:** off-topic input → friendly fallback with **no citations** (`debug.grounded:false`);
non-English `language` is routed and tracked (mock AI returns English answer text — real Sarvam/Gemma
translate when wired).

**Errors:** `401 Missing/Invalid/Expired session token` · `429` rate limit or daily quota.

### `POST /api/v1/search`
Knowledge search (reuses the RAG pipeline). Body `{ "query", "language?" }`. → same `ChatResponse`
shape with `intent:"search"`.

### `POST /api/v1/filings`
Filing-scoped knowledge (filters retrieval to `NSE`/`BSE`/`NALCO_IR`). Body
`{ "query", "company?", "language?" }`. → `intent:"filing"`.

### `POST /api/v1/stock`
Direct market quote (reuses the market service). Body `{ "symbol", "language?" }`. →
`branch:"market"`, `debug.data` = quote.

All three module endpoints require the session Bearer token and pass the same security gate as `/chat`.

---

## Admin plane

### `POST /api/v1/admin/login`
```bash
curl -s -X POST $B/api/v1/admin/login -H "Content-Type: application/json" \
  -d '{"email":"admin@brokerassist.local","password":"admin12345"}'
```
**200** → `{ "admin_token": "<JWT>", "expires_in": 3600, "role": "superadmin" }`
**Errors:** `401 Invalid credentials` (generic — no user enumeration) · `423 Account temporarily
locked` (after `BA_ADMIN_MAX_FAILED_LOGINS` failures).

All admin calls below require `Authorization: Bearer <admin_token>`. **Every write is audited.**

| Method & path | Role | Purpose |
|---|---|---|
| `GET /api/v1/admin/me` | admin | Current admin identity |
| `GET /api/v1/admin/tenants` | admin | List tenants |
| `POST /api/v1/admin/tenants` | **superadmin** | Create a tenant `{name, daily_quota}` |
| `GET /api/v1/admin/tenants/{id}/api-keys` | admin | List a tenant's keys (prefix + status) |
| `POST /api/v1/admin/tenants/{id}/api-keys` | admin | Mint a key — **raw key returned once** as `api_key` |
| `POST /api/v1/admin/api-keys/{id}/revoke` | admin | Revoke a key |
| `GET /api/v1/admin/tenants/{id}/allowlist` | admin | List allowed Origins |
| `POST /api/v1/admin/tenants/{id}/allowlist` | admin | Add an Origin `{domain}` |
| `DELETE /api/v1/admin/allowlist/{id}` | admin | Remove an Origin |
| `GET /api/v1/admin/tenants/{id}/quota` | admin | Quota + today's usage |
| `PUT /api/v1/admin/tenants/{id}/quota` | admin | Update daily quota `{daily_quota}` |
| `GET /api/v1/admin/abuse` | admin | Last 50 abuse events |
| `GET /api/v1/admin/audit` | admin | Last 50 admin audit entries |

```bash
ATOK=$(curl -s -X POST $B/api/v1/admin/login -H "Content-Type: application/json" \
  -d '{"email":"admin@brokerassist.local","password":"admin12345"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['admin_token'])")
curl -s $B/api/v1/admin/tenants -H "Authorization: Bearer $ATOK"
```

---

## Response envelope (`ChatResponse`)

Shared by `/chat`, `/search`, `/filings`, `/stock`:

| Field | Type | Notes |
|---|---|---|
| `answer` | string | Reply text, in the user's language |
| `language` | string | Resolved language (`en`/`hi`/`ta`) |
| `intent` | string | e.g. `knowledge_general`, `filing_dividend`, `market_data`, `search` |
| `branch` | string | `"market"` or `"knowledge"` |
| `citations` | `Citation[]` | `{document_id, chunk_id, source, title, url, filing_date}` — empty for market/off-topic |
| `disclaimer` | string | Always `"Informational only — not investment advice."` |
| `debug` | object | Pipeline/branch diagnostics |

## Status codes

| Code | When |
|---|---|
| `200` | Success |
| `401` | Missing/invalid/expired token, bad widget key, bad admin credentials |
| `403` | Origin not allowlisted; superadmin required |
| `404` | Unknown tenant / key / domain |
| `422` | Request body fails schema validation |
| `423` | Admin account locked |
| `429` | Rate limit or daily quota exceeded |

Every response carries an **`X-Request-ID`** header for log correlation.
