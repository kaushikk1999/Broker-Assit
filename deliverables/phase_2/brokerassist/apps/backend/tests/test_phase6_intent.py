"""Phase 6 intent taxonomy + routing fork + company-filter derivation."""
from app.services.intent_router import classify, knowledge_intent


def test_market_query_routes_to_market_no_filters():
    r = classify("What is the LTP of NALCO?")
    assert r["branch"] == "market"
    assert r["intent"] == "market_data"
    assert r["symbol"] == "NALCO"
    assert r["filters"] is None


def test_disclosure_query_derives_company_filter():
    r = classify("Explain NALCO's latest quarterly result")
    assert r["branch"] == "knowledge"
    assert r["intent"] == "disclosure"
    assert r["filters"] == {"company": "NALCO"}


def test_algo_query_intent_no_company():
    r = classify("difference between white box and black box algos")
    assert r["branch"] == "knowledge"
    assert r["intent"] == "algo"
    assert r["filters"] is None  # no company mentioned → no over-filtering


def test_navigation_query_intent():
    r = classify("How do I open an account on your website?")
    assert r["branch"] == "knowledge"
    assert r["intent"] == "navigation"


def test_faq_query_intent():
    r = classify("What is a mutual fund?")
    assert r["branch"] == "knowledge"
    assert r["intent"] == "faq"


def test_greeting_is_general_no_filter():
    r = classify("hello there")
    assert r["branch"] == "knowledge"
    assert r["intent"] == "knowledge_general"
    assert r["filters"] is None


def test_company_detected_in_english_name():
    r = classify("Tell me about National Aluminium dividends")
    assert r["filters"] == {"company": "NALCO"}
    assert r["intent"] == "disclosure"


def test_knowledge_intent_public_sub_classifier():
    # public sub-classifier used by the RAG pipeline on the TRANSLATED English query
    assert knowledge_intent("NALCO quarterly result") == "disclosure"
    assert knowledge_intent("white box vs black box algo") == "algo"
    assert knowledge_intent("how do I open an account") == "navigation"
    assert knowledge_intent("what is a mutual fund?") == "faq"
    assert knowledge_intent("hello there") == "knowledge_general"
