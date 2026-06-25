"""Discrete module endpoints (roadmap modules) — thin wrappers reusing the Phase 2 services.
Search & Filings reuse the knowledge RAG pipeline; Stock reuses the market service."""
from fastapi import APIRouter, Depends, Request

from app.config import settings
from app.core.security import require_session
from app.core.ratelimit import client_ip, check_rate_limits, check_and_increment_quota
from app.adapters import get_language
from app.services.rag_pipeline import handle_knowledge, DISCLAIMER
from app.services.market_service import handle_market
from app.services.persistence import persist_turn, log_event
from app.schemas.modules import SearchRequest, FilingsRequest, StockRequest
from app.schemas.chat import ChatResponse

router = APIRouter(prefix="/api/v1", tags=["modules"])


def _guard(request: Request, ctx: dict) -> tuple[str, int, str]:
    session_id, tenant_id, db = ctx["session_id"], ctx["tenant_id"], ctx["db"]
    ip = client_ip(request)
    check_rate_limits(db, session_id, tenant_id, ip)
    check_and_increment_quota(db, tenant_id, ip)
    return session_id, tenant_id, ip


def _lang(text: str, hint: str | None) -> str:
    return hint if hint in settings.supported_languages else get_language().detect(text)


@router.post("/search", response_model=ChatResponse)
def search(body: SearchRequest, request: Request, ctx: dict = Depends(require_session)):
    session_id, tenant_id, _ = _guard(request, ctx)
    db = ctx["db"]; lang = _lang(body.query, body.language)
    res = handle_knowledge(body.query, lang, db)
    log_event(db, "search", tenant_id, session_id, {"results": len(res["citations"])})
    persist_turn(db, tenant_id, session_id, body.query, res["answer"], lang, "search", "knowledge")
    return ChatResponse(answer=res["answer"], language=lang, intent="search", branch="knowledge",
                        citations=res["citations"], disclaimer=DISCLAIMER, debug=res["debug"])


@router.post("/filings", response_model=ChatResponse)
def filings(body: FilingsRequest, request: Request, ctx: dict = Depends(require_session)):
    session_id, tenant_id, _ = _guard(request, ctx)
    db = ctx["db"]; lang = _lang(body.query, body.language)
    filters = {"source": ["NSE", "BSE", "NALCO_IR"]}
    if body.company:
        filters["company"] = body.company
    res = handle_knowledge(body.query, lang, db, filters=filters)
    log_event(db, "filings", tenant_id, session_id, {"company": body.company})
    persist_turn(db, tenant_id, session_id, body.query, res["answer"], lang, "filing", "knowledge")
    return ChatResponse(answer=res["answer"], language=lang, intent="filing", branch="knowledge",
                        citations=res["citations"], disclaimer=DISCLAIMER, debug=res["debug"])


@router.post("/stock", response_model=ChatResponse)
def stock(body: StockRequest, request: Request, ctx: dict = Depends(require_session)):
    session_id, tenant_id, _ = _guard(request, ctx)
    db = ctx["db"]; lang = body.language if body.language in settings.supported_languages else "en"
    res = handle_market(body.symbol, lang)
    log_event(db, "stock", tenant_id, session_id, {"symbol": body.symbol})
    return ChatResponse(answer=res["answer"], language=lang, intent="market_data", branch="market",
                        citations=[], disclaimer=DISCLAIMER,
                        debug={"cache_hit": res["cache_hit"], "data": res["data"]})
