"""Phase 3 tests: admin auth, api-key mgmt, allowlist, module endpoints, abuse, persistence."""
from fastapi.testclient import TestClient
from app.main import app
from app.db.seed import seed

seed()
client = TestClient(app)
GOOD_ORIGIN = {"Origin": "http://localhost"}


def _session_token(widget_key="demo-public-key", origin=GOOD_ORIGIN):
    r = client.post("/api/v1/session", json={"widget_key": widget_key}, headers=origin)
    assert r.status_code == 200, r.text
    return r.json()["session_token"]


def _admin_token(email="admin@brokerassist.local", password="admin12345"):
    r = client.post("/api/v1/admin/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["admin_token"]


def _sauth(t):
    return {"Authorization": f"Bearer {t}"}


# ---- admin auth ----
def test_admin_login_and_me():
    tok = _admin_token()
    me = client.get("/api/v1/admin/me", headers=_sauth(tok))
    assert me.status_code == 200
    assert me.json()["role"] == "superadmin"


def test_admin_login_bad_password():
    r = client.post("/api/v1/admin/login", json={"email": "admin@brokerassist.local", "password": "wrong"})
    assert r.status_code == 401


def test_admin_endpoints_require_token():
    assert client.get("/api/v1/admin/tenants").status_code == 401
    assert client.get("/api/v1/admin/me").status_code == 401


# ---- api key lifecycle ----
def test_create_tenant_and_apikey_then_authenticate():
    tok = _admin_token()
    # create tenant (superadmin)
    r = client.post("/api/v1/admin/tenants", json={"name": "Acme Broking", "daily_quota": 100},
                    headers=_sauth(tok))
    assert r.status_code == 200, r.text
    tid = r.json()["id"]
    # mint an api key
    r = client.post(f"/api/v1/admin/tenants/{tid}/api-keys", headers=_sauth(tok))
    assert r.status_code == 200, r.text
    raw = r.json()["api_key"]
    assert raw.startswith("ba_")
    # new tenant has no allowlist → any origin allowed; session should succeed
    s = client.post("/api/v1/session", json={"widget_key": raw}, headers={"Origin": "https://acme.example"})
    assert s.status_code == 200, s.text
    # revoke → key no longer works
    kid = client.get(f"/api/v1/admin/tenants/{tid}/api-keys", headers=_sauth(tok)).json()[0]["id"]
    assert client.post(f"/api/v1/admin/api-keys/{kid}/revoke", headers=_sauth(tok)).status_code == 200
    s2 = client.post("/api/v1/session", json={"widget_key": raw}, headers={"Origin": "https://acme.example"})
    assert s2.status_code == 401


def test_allowlist_management():
    tok = _admin_token()
    tid = client.get("/api/v1/admin/tenants", headers=_sauth(tok)).json()[0]["id"]
    r = client.post(f"/api/v1/admin/tenants/{tid}/allowlist", json={"domain": "demo.example.com"},
                    headers=_sauth(tok))
    assert r.status_code == 200
    domains = [d["domain"] for d in client.get(f"/api/v1/admin/tenants/{tid}/allowlist",
                                               headers=_sauth(tok)).json()]
    assert "demo.example.com" in domains


# ---- module endpoints ----
def test_search_endpoint_returns_citations():
    t = _session_token()
    r = client.post("/api/v1/search", json={"query": "NALCO quarterly result"}, headers=_sauth(t))
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["intent"] == "search" and body["branch"] == "knowledge"
    assert len(body["citations"]) >= 1


def test_filings_endpoint():
    t = _session_token()
    r = client.post("/api/v1/filings", json={"query": "NALCO dividend", "company": "NALCO"},
                    headers=_sauth(t))
    assert r.status_code == 200
    assert r.json()["branch"] == "knowledge"


def test_stock_endpoint_is_market_branch():
    t = _session_token()
    r = client.post("/api/v1/stock", json={"symbol": "NALCO"}, headers=_sauth(t))
    assert r.status_code == 200
    body = r.json()
    assert body["branch"] == "market" and body["citations"] == []
    assert "trading at" in body["answer"].lower()


# ---- abuse / persistence visibility ----
def test_per_session_rate_limit_and_abuse_logged():
    t = _session_token()
    codes = [client.post("/api/v1/chat", json={"message": "hi"}, headers=_sauth(t)).status_code
             for _ in range(25)]
    assert 429 in codes  # per-session limit (20/min) trips
    # the breach should be recorded and visible to admin
    tok = _admin_token()
    abuse = client.get("/api/v1/admin/abuse", headers=_sauth(tok)).json()
    assert any(e["kind"] == "rate_limit" for e in abuse)


def test_quota_get_and_update():
    tok = _admin_token()
    tid = client.get("/api/v1/admin/tenants", headers=_sauth(tok)).json()[0]["id"]
    assert client.put(f"/api/v1/admin/tenants/{tid}/quota", json={"daily_quota": 9999},
                      headers=_sauth(tok)).status_code == 200
    q = client.get(f"/api/v1/admin/tenants/{tid}/quota", headers=_sauth(tok)).json()
    assert q["daily_quota"] == 9999


def test_ready_reports_dependencies():
    rd = client.get("/ready").json()
    assert "dependencies" in rd
    assert rd["dependencies"]["redis"]["backend"] in ("memory", "redis")
    assert rd["dependencies"]["qdrant"]["configured"] is False
