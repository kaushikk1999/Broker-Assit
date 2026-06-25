"""Public widget endpoints: issue a session token, then chat through the intent-routed pipeline."""
from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session as DBSession

from app.db.base import get_db
from app.db import models
from app.config import settings
from app.core.security import (
    authenticate_widget, issue_session_token, new_session_id, require_session,
)
from app.core.ratelimit import client_ip, check_rate_limits, check_and_increment_quota
from app.adapters import get_language
from app.services.intent_router import classify
from app.services.market_service import handle_market
from app.services.rag_pipeline import handle_knowledge, DISCLAIMER
from app.services.persistence import persist_turn, log_event
from app.schemas.chat import SessionRequest, SessionResponse, ChatRequest, ChatResponse

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/session", response_model=SessionResponse)
def create_session(body: SessionRequest, request: Request, origin: str | None = Header(None),
                   db: DBSession = Depends(get_db)):
    tenant = authenticate_widget(body.widget_key, origin, db)
    sid = new_session_id()
    db.add(models.Session(id=sid, tenant_id=tenant.id, ip=client_ip(request)))
    db.commit()
    log_event(db, "session_created", tenant.id, sid)
    token = issue_session_token(tenant.id, sid)
    return SessionResponse(session_token=token, expires_in=settings.session_ttl_seconds)


@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest, request: Request, ctx: dict = Depends(require_session)):
    session_id, tenant_id, db = ctx["session_id"], ctx["tenant_id"], ctx["db"]
    ip = client_ip(request)

    # Abuse & cost control BEFORE any LLM/translation call (roadmap principle).
    check_rate_limits(db, session_id, tenant_id, ip)
    check_and_increment_quota(db, tenant_id, ip)

    lang = body.language if body.language in settings.supported_languages else get_language().detect(body.message)
    route = classify(body.message)

    if route["branch"] == "market":
        result = handle_market(route["symbol"], lang)
        answer = result["answer"]
        persist_turn(db, tenant_id, session_id, body.message, answer, lang, route["intent"], "market")
        log_event(db, "chat", tenant_id, session_id, {"branch": "market"})
        return ChatResponse(answer=answer, language=lang, intent=route["intent"], branch="market",
                            citations=[], disclaimer=DISCLAIMER,
                            debug={"cache_hit": result["cache_hit"], "data": result["data"]})

    result = handle_knowledge(body.message, lang, db, filters=route.get("filters"))
    persist_turn(db, tenant_id, session_id, body.message, result["answer"], lang, route["intent"],
                 "knowledge")
    log_event(db, "chat", tenant_id, session_id, {"branch": "knowledge",
                                                  "citations": len(result["citations"])})
    return ChatResponse(answer=result["answer"], language=lang, intent=route["intent"],
                        branch="knowledge", citations=result["citations"], disclaimer=DISCLAIMER,
                        debug=result["debug"])
