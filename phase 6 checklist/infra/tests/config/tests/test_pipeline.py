"""End-to-end tests for the Phase 2 thin-slice (mocks-first). Run: pytest -q"""
import os
import tempfile

os.environ.setdefault("BA_DATABASE_URL", f"sqlite:///{tempfile.gettempdir()}/ba_test.db")

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from app.db.seed import seed  # noqa: E402

seed()  # ensure tables + demo data exist (lifespan doesn't fire without the context manager)
client = TestClient(app)
GOOD_ORIGIN = {"Origin": "http://localhost"}


def _token():
    r = client.post("/api/v1/session", json={"widget_key": "demo-public-key"}, headers=GOOD_ORIGIN)
    assert r.status_code == 200, r.text
    return r.json()["session_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_health_and_ready():
    assert client.get("/health").json()["status"] == "ok"
    rd = client.get("/ready").json()
    assert rd["tenants"] >= 1 and rd["documents"] >= 4


def test_widget_auth_rejects_bad_key():
    r = client.post("/api/v1/session", json={"widget_key": "nope"}, headers=GOOD_ORIGIN)
    assert r.status_code == 401


def test_widget_auth_rejects_bad_origin():
    r = client.post("/api/v1/session", json={"widget_key": "demo-public-key"},
                    headers={"Origin": "http://evil.example"})
    assert r.status_code == 403


def test_chat_requires_session():
    r = client.post("/api/v1/chat", json={"message": "hi"})
    assert r.status_code == 401


def test_knowledge_query_returns_citation_english():
    r = client.post("/api/v1/chat", json={"message": "Explain NALCO's latest quarterly result"},
                    headers=_auth(_token()))
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["branch"] == "knowledge"
    assert "NALCO" in body["answer"]
    assert len(body["citations"]) >= 1
    assert body["citations"][0]["source"] in {"NALCO_IR", "NSE"}


def test_knowledge_query_tamil_translates_and_cites():
    r = client.post("/api/v1/chat",
                    json={"message": "NALCO இன் சமீபத்திய காலாண்டு முடிவை விளக்குங்கள்", "language": "ta"},
                    headers=_auth(_token()))
    body = r.json()
    assert body["language"] == "ta"
    assert any(ch in body["answer"] for ch in "அஆஇ")  # Tamil script present
    assert len(body["citations"]) >= 1


def test_market_query_bypasses_rag():
    r = client.post("/api/v1/chat", json={"message": "What is the LTP of NALCO?"},
                    headers=_auth(_token()))
    body = r.json()
    assert body["branch"] == "market"
    assert body["citations"] == []
    assert "trading at" in body["answer"].lower()


def test_greeting_has_no_spurious_citations():
    r = client.post("/api/v1/chat", json={"message": "hello there"}, headers=_auth(_token()))
    body = r.json()
    assert body["branch"] == "knowledge"
    assert body["citations"] == []  # chit-chat must not cite filings
    assert body["debug"].get("grounded") is False


def test_algo_query_routes_to_knowledge():
    r = client.post("/api/v1/chat",
                    json={"message": "difference between white box and black box algos"},
                    headers=_auth(_token()))
    body = r.json()
    assert body["branch"] == "knowledge"
    assert len(body["citations"]) >= 1
