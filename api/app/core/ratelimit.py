"""Abuse & cost control (roadmap Phase 3). Redis-backed atomic counters (in-memory fallback in dev).
Per-session + per-IP rate limits and per-tenant daily quota are all enforced BEFORE any LLM/translation
call. Breaches are recorded in abuse_events. Quota also persists to PostgreSQL (durable backstop)."""
from datetime import date

from fastapi import HTTPException, Request
from sqlalchemy.orm import Session as DBSession

from app.config import settings
from app.core.redis import cache, k
from app.db import models


def client_ip(request: Request) -> str:
    """Proxy-aware (Railway sits behind a proxy): first hop of X-Forwarded-For, else peer."""
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "0.0.0.0"


def record_abuse(db: DBSession, kind: str, *, tenant_id=None, session_id=None, ip="", detail="") -> None:
    db.add(models.AbuseEvent(kind=kind, tenant_id=tenant_id, session_id=session_id, ip=ip, detail=detail))
    db.commit()


def check_rate_limits(db: DBSession, session_id: str, tenant_id: int, ip: str) -> None:
    sess = cache.incr(k("ratelimit", "sess", session_id), 60)
    if sess > settings.rate_limit_per_session_per_min:
        record_abuse(db, "rate_limit", tenant_id=tenant_id, session_id=session_id, ip=ip,
                     detail="per-session/min")
        raise HTTPException(status_code=429, detail="Rate limit: too many messages, slow down.")
    ipc = cache.incr(k("ratelimit", "ip", ip), 60)
    if ipc > settings.rate_limit_per_ip_per_min:
        record_abuse(db, "rate_limit", tenant_id=tenant_id, session_id=session_id, ip=ip,
                     detail="per-ip/min")
        raise HTTPException(status_code=429, detail="Rate limit: too many requests from this network.")


def check_and_increment_quota(db: DBSession, tenant_id: int, ip: str = "") -> int:
    """Per-tenant daily quota: Redis hot counter (enforcement) + PostgreSQL durable record."""
    today = date.today()
    # durable backstop
    row = db.query(models.UsageQuota).filter_by(tenant_id=tenant_id, day=today).first()
    if not row:
        row = models.UsageQuota(tenant_id=tenant_id, day=today, count=0)
        db.add(row)
        db.flush()
    tenant = db.get(models.Tenant, tenant_id)
    cap = (tenant.daily_quota if tenant else 0) or settings.tenant_daily_quota
    # hot counter
    hot = cache.incr(k("quota", str(tenant_id), today.isoformat()), 172800)
    row.count = max(row.count + 1, hot)
    db.commit()
    if hot > cap:
        record_abuse(db, "quota", tenant_id=tenant_id, ip=ip, detail=f"daily cap {cap}")
        raise HTTPException(status_code=429, detail="Daily quota reached for this brokerage.")
    return hot
