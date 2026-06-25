"""Branch B — canonical RAG pipeline (roadmap Phase 6/7):
detect → translate query→EN → embed → hybrid retrieve (dense+sparse, filtered) → RRF → Top-20
→ cross-encoder rerank → Top-5 → context → Gemma → translate response → citations (from PostgreSQL)."""
import re

from sqlalchemy.orm import Session as DBSession

from app.config import settings
from app.adapters import get_language, get_embedding, get_vector_store, get_reranker, get_llm
from app.services.query_expansion import expand_query
from app.db import models
from app.schemas.chat import Citation

DISCLAIMER = "Informational only — not investment advice."

# Friendly fallback when retrieval has no meaningful overlap (chit-chat, off-topic).
NO_GROUNDING = {
    "en": "I can help with stock information, filing explanations, and algo-trading education — "
          "all with sources. Try asking about a stock, a NALCO filing, or white-box vs black-box algos.",
    "hi": "मैं स्टॉक जानकारी, फाइलिंग की व्याख्या और एल्गो-ट्रेडिंग शिक्षा में मदद कर सकता हूँ — सभी स्रोत के साथ। "
          "किसी स्टॉक, NALCO फाइलिंग, या व्हाइट-बॉक्स बनाम ब्लैक-बॉक्स एल्गो के बारे में पूछें।",
    "ta": "பங்கு தகவல், தாக்கல் விளக்கம், அல்கோ-வர்த்தக கல்வி ஆகியவற்றில் உதவ முடியும் — அனைத்தும் ஆதாரத்துடன். "
          "ஒரு பங்கு, NALCO தாக்கல், அல்லது வைட்-பாக்ஸ் vs பிளாக்-பாக்ஸ் அல்கோ பற்றி கேளுங்கள்.",
}
_STOP = {"the", "a", "an", "is", "are", "of", "to", "in", "on", "for", "and", "or", "what",
         "how", "explain", "me", "my", "your", "please", "hi", "hello", "hey", "there",
         "about", "tell", "can", "you", "give", "show", "latest"}


def _content_tokens(text: str) -> set[str]:
    toks = re.findall(r"[a-z0-9]+", text.lower())
    return {t for t in toks if t not in _STOP and len(t) > 2}


def _is_relevant(query_en: str, chunk_texts: list[str]) -> bool:
    q = _content_tokens(query_en)
    if not q:
        return False
    body = set()
    for txt in chunk_texts:
        body |= _content_tokens(txt)
    return bool(q & body)


def _load_chunks(db: DBSession) -> list[tuple[int, int, str, dict]]:
    """Chunks for the mock store as (document_id, chunk_id, text, payload). The payload is the SAME
    canonical FK + filter dict the embedding pipeline writes to Qdrant (built via the metadata
    contract), so the mock filters identically to the real Qdrant adapter."""
    from app.services.metadata_contract import build_payload
    rows: list[tuple[int, int, str, dict]] = []
    for c in db.query(models.DocumentChunk).all():
        doc = db.get(models.Document, c.document_id)
        payload = build_payload(
            document_id=c.document_id, chunk_id=c.id, language=c.lang,
            company=(doc.company if doc else ""),
            filing_type=(doc.filing_type if doc else ""),
            filing_date=(doc.filing_date if doc else None),
            strict=False,
        )
        rows.append((c.document_id, c.id, c.text, payload))
    return rows


def _hydrate_text(db: DBSession, candidates: list) -> list:
    """Fill chunk text from PostgreSQL for candidates that arrived with only FKs (real Qdrant read).

    Candidates whose chunk no longer exists in the registry are dropped (cannot ground or cite without
    text). Candidates that already carry text (the mock store) pass through unchanged."""
    hydrated = []
    for c in candidates:
        if c.text:
            hydrated.append(c)
            continue
        chunk = db.get(models.DocumentChunk, c.chunk_id)
        if chunk is None:
            continue
        c.text = chunk.text
        hydrated.append(c)
    return hydrated


def handle_knowledge(message: str, user_lang: str, db: DBSession, filters: dict | None = None) -> dict:
    language = get_language()
    embedding = get_embedding()
    reranker = get_reranker()
    llm = get_llm()

    # 1) Normalize/translate the query to English BEFORE retrieval (fixes HI/TA retrieval).
    query_en = language.translate(message, target="en", source=user_lang) if user_lang != "en" else message
    # 1b) Query expansion (recall only): append canonical synonyms for retrieval. Reranking and
    # generation use the original question (precision), so expansion never skews answer quality.
    query_retrieval = expand_query(query_en)
    # 2) Query embedding (Ollama Cloud · embeddinggemma in prod).
    query_vec = embedding.embed(query_retrieval)
    # 3) Hybrid retrieval (dense + native sparse) with filters at retrieval → RRF → Top-20.
    store = get_vector_store(_load_chunks(db))
    candidates = store.hybrid_search(query_retrieval, query_vec, top_k=settings.retrieve_top_k,
                                     filters=filters)
    # 3b) Hydrate chunk text from PostgreSQL for candidates that carry only FKs (real Qdrant read).
    # Keeps the citation invariant: Qdrant payload is FK-only; text/citations come from PostgreSQL.
    candidates = _hydrate_text(db, candidates)
    # 4) Cross-encoder rerank → Top-5 (on the user's actual question, not the expanded query).
    top = reranker.rerank(query_en, candidates, top_k=settings.rerank_top_k)
    # 4b) Relevance gate: if nothing meaningfully overlaps the query (chit-chat / off-topic),
    # return a friendly fallback with NO citations rather than citing unrelated filings.
    if not _is_relevant(query_en, [c.text for c in top]):
        lang = user_lang if user_lang in NO_GROUNDING else "en"
        return {"answer": NO_GROUNDING[lang], "citations": [],
                "debug": {"query_en": query_en, "query_retrieval": query_retrieval,
                          "grounded": False, "retrieved": len(candidates),
                          "filters": filters or None}}
    # 5) Context assembly + generation (Gemma).
    context = [c.text for c in top]
    answer_en = llm.generate(query_en, context)
    # 6) Translate response back to the user's language.
    answer = language.translate(answer_en, target=user_lang) if user_lang != "en" else answer_en
    # 7) Citations resolved from PostgreSQL (NEVER from the vector store).
    citations: list[Citation] = []
    for c in top[:3]:
        doc = db.get(models.Document, c.document_id)
        if doc:
            citations.append(Citation(
                document_id=doc.id, chunk_id=c.chunk_id, source=doc.source,
                title=doc.title, url=doc.url,
                filing_date=doc.filing_date.isoformat() if doc.filing_date else None,
            ))
    return {
        "answer": answer,
        "citations": citations,
        "debug": {"query_en": query_en, "query_retrieval": query_retrieval,
                  "retrieved": len(candidates), "reranked": len(top), "filters": filters or None},
    }
