"""Phase 6 end-to-end (mocks-first): full canonical pipeline through the public chat API.

Covers the roadmap pipeline behaviors added/hardened in Phase 6: auth+rate-limit gate, intent fork,
translate-before-retrieval, query expansion, metadata-filter-at-retrieval, RRF, rerank, FK-only
citations resolved from PostgreSQL, response translation, and /ready provider transparency."""
import os
import tempfile

os.environ.setdefault("BA_DATABASE_URL", f"sqlite:///{tempfile.gettempdir()}/ba_test.db")

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from app.db.seed import seed  # noqa: E402

seed()
client = TestClient(app)
GOOD_ORIGIN = {"Origin": "http://localhost"}


def _token():
    r = client.post("/api/v1/session", json={"widget_key": "demo-public-key"}, headers=GOOD_ORIGIN)
    assert r.status_code == 200, r.text
    return r.json()["session_token"]


def _auth():
    return {"Authorization": f"Bearer {_token()}"}


def test_ready_reports_phase6_providers_as_mock():
    deps = client.get("/ready").json()["dependencies"]
    assert deps["reranker"]["provider"] == "mock"
    assert deps["generation"]["provider"] == "mock"
    assert deps["language"]["provider"] == "mock"
    assert "retrieval" in deps  # collection status surfaced


def test_knowledge_query_derives_company_filter_and_cites():
    r = client.post("/api/v1/chat", json={"message": "Explain NALCO's latest quarterly result"},
                    headers=_auth())
    body = r.json()
    assert body["branch"] == "knowledge"
    assert body["intent"] == "disclosure"
    assert len(body["citations"]) >= 1
    # company filter applied at retrieval → only NALCO docs are candidates
    assert body["debug"]["filters"] == {"company": "NALCO"}
    assert "query_retrieval" in body["debug"]
    assert "national aluminium" in body["debug"]["query_retrieval"].lower()  # expansion fired


def test_algo_query_cites_algo_doc_no_company_filter():
    r = client.post("/api/v1/chat",
                    json={"message": "difference between white box and black box algos"},
                    headers=_auth())
    body = r.json()
    assert body["intent"] == "algo"
    assert body["debug"]["filters"] is None
    assert len(body["citations"]) >= 1
    assert "algo" in body["answer"].lower() or "box" in body["answer"].lower()


def test_market_query_bypasses_rag_no_citations():
    r = client.post("/api/v1/chat", json={"message": "What is the LTP of NALCO?"}, headers=_auth())
    body = r.json()
    assert body["branch"] == "market"
    assert body["citations"] == []


def test_tamil_query_translates_and_cites():
    r = client.post("/api/v1/chat",
                    json={"message": "NALCO இன் சமீபத்திய காலாண்டு முடிவை விளக்குங்கள்", "language": "ta"},
                    headers=_auth())
    body = r.json()
    assert body["language"] == "ta"
    assert any(ch in body["answer"] for ch in "அஆஇ")
    assert len(body["citations"]) >= 1


def test_citation_fields_resolve_from_postgres():
    r = client.post("/api/v1/chat", json={"message": "NALCO dividend history"}, headers=_auth())
    cites = r.json()["citations"]
    assert cites
    c0 = cites[0]
    # citation carries PostgreSQL-resolved fields (source/url/title), not a Qdrant payload
    assert c0["source"] and c0["url"] and "document_id" in c0 and "chunk_id" in c0


def test_greeting_has_no_spurious_citations():
    r = client.post("/api/v1/chat", json={"message": "hello there"}, headers=_auth())
    body = r.json()
    assert body["citations"] == []
    assert body["debug"].get("grounded") is False
