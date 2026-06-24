# Security & Abuse Control

BrokerAssist exposes a **public, anonymous widget** embedded on third-party brokerage sites. That makes
the security model the load-bearing part of the backend. The governing rule (ADR-005):

> **Every rate-limit, quota, and auth check runs *before* any LLM / translation call** — so abuse and
> runaway cost are bounded at the edge, not after paying a vendor.

See the [request-lifecycle diagram](../diagrams/request-lifecycle.svg) for the visual flow.

---

## 1. Two trust planes

| | Widget session plane | Admin plane |
|---|---|---|
| Who | Anonymous end-investors | Brokerage operators |
| Establish trust | Widget key + Origin allowlist | Email + password (bcrypt) |
| Token | Session JWT, 30-min TTL | Admin JWT, 1-hr TTL, `typ:"admin"` |
| Secret | `BA_SESSION_JWT_SECRET` | `BA_ADMIN_JWT_SECRET` |
| Code | `core/security.py` | `core/admin_security.py`, `api/routes_admin.py` |

The two planes use **separate secrets and separate token types** — an admin token can't be used as a
session token and vice-versa (`require_admin` checks `payload.typ == "admin"`).

---

## 2. Widget authentication (`core/security.py`)

A session is issued by `POST /session` only when **both** checks pass:

1. **Widget key by hash.** The public key is never stored in plaintext — `api_keys` holds a
   **SHA-256 hash** (`key_hash`) plus an 8-char `key_prefix` for lookup/rotation UX. Lookup requires
   `status="active"`; the tenant must be `is_active`. Failure → `401 Invalid widget key`.
2. **Origin allowlist.** The request `Origin` host is matched against the tenant's `domain_allowlist`:
   exact `host[:port]`, or a `*.` subdomain wildcard (`*.acme.com` matches `app.acme.com` and
   `acme.com`). Mismatch → `403 Origin '…' not allowlisted`.

On success the visitor gets a **signed session JWT** (`{sub: session_id, tid: tenant_id, iat, exp}`),
and a `sessions` row is recorded. Every later call carries `Authorization: Bearer <token>`;
`require_session` decodes it and resolves `tenant_id` + `session_id` (`401` on missing/invalid/expired).

> CORS at the edge is permissive (`allow_origins=["*"]`) **by design** — the widget is embedded
> cross-origin, so the real trust boundary is the per-tenant Origin allowlist enforced at `/session`,
> not the browser CORS header.

---

## 3. Abuse & cost control (`core/ratelimit.py`)

Enforced inside `/chat` (and every module endpoint) **before** routing/model calls:

| Control | Default | Window | Backed by |
|---|---|---|---|
| Per-session rate | `20` / min | 60 s | Redis `INCR`+`EXPIRE` (atomic) |
| Per-IP rate | `40` / min | 60 s | Redis counter |
| Per-tenant daily quota | `5000` / day (per-tenant override) | day | Redis **hot counter** + PostgreSQL **durable backstop** |

- Counters use **atomic `INCR` with `EXPIRE` on first hit**; in dev they fall back to a process-local
  in-memory backend with the same interface (`core/redis.py`).
- The daily quota writes both a Redis hot counter (enforcement) and a `usage_quotas` row (durable
  record that survives a Redis flush).
- `client_ip()` is **proxy-aware** — it reads the first hop of `X-Forwarded-For` (Railway sits behind a
  proxy), falling back to the socket peer.
- Any breach is recorded in `abuse_events` (`kind` = `rate_limit` / `quota` / …) and surfaced to
  operators via `GET /admin/abuse`. Breach response: **`429`**.

**Verified:** firing 25 rapid messages on one session yields exactly **20 × 200 then 5 × 429** (see
[TESTING.md](TESTING.md)).

---

## 4. Admin authentication (`core/admin_security.py`)

- **Passwords** are hashed with **bcrypt** (`hash_password` / `verify_password`).
- **Login lockout:** after `BA_ADMIN_MAX_FAILED_LOGINS` (default 5) failures, the account is locked for
  `BA_ADMIN_LOCKOUT_SECONDS` (default 900 s) → `423 Account temporarily locked`.
- **No user enumeration:** unknown email and wrong password both return the same generic
  `401 Invalid credentials`.
- **Roles:** `require_admin` and `require_superadmin` dependencies gate routes (e.g. creating a tenant
  needs superadmin).
- **Audit:** every admin write calls `audit(...)` → an `admin_audit_log` row (`action`, `target`,
  `detail`, `ip`). Surfaced via `GET /admin/audit`.

---

## 5. Secret & key hygiene

- **API keys:** generated as `ba_<token_urlsafe(24)>` (`admin_service.generate_api_key`); the raw value
  is shown **once** on creation (`ApiKeyCreated.api_key`) and never stored or returned again — only the
  hash + prefix persist. Revocation flips `status` to `revoked` and stamps `revoked_at`.
- **JWT secrets** default to `dev-only-change-me*` — **must be overridden in production**.
- **`.env` is git-ignored** (root `.gitignore`); `*.example` files are kept. Rotate any key ever shared
  in plaintext (the brokerassist README explicitly calls out the Qdrant/Ollama keys).

---

## 6. Compliance posture

- **Every assistant answer** carries the disclaimer *"Informational only — not investment advice."*
- **Knowledge answers are cited** from the PostgreSQL registry, and **off-topic inputs return no
  fabricated citations** (the RAG relevance gate). This citations + disclaimer requirement came
  directly out of the Phase 0 finding that finance answers are SEBI/NSE-sensitive.

---

## 7. Threats addressed vs. deferred

| Addressed today | Deferred / next |
|---|---|
| Key theft (hashed at rest, revocable) | WAF / bot-fingerprinting (`abuse_events.kind` reserves `bot`) |
| Cross-site key reuse (Origin allowlist) | Per-key (vs per-tenant) quotas |
| Brute-force admin login (lockout) | MFA for admins |
| Runaway cost / floods (rate + quota, pre-LLM) | Distributed rate-limit tuning at scale |
| Citation integrity (Postgres source of truth) | Source-authority precedence on conflict (open ADR-009) |
