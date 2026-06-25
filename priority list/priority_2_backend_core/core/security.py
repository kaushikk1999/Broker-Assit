"""Widget origin auth + anonymous signed session tokens (roadmap Phase 3 widget security).

API keys are looked up by SHA-256 hash from the api_keys table; the Origin host is matched against
the per-tenant domain_allowlist table (exact host[:port], or '*.' subdomain wildcard)."""
import hashlib
import time
import uuid
from urllib.parse import urlparse

import jwt
from fastapi import HTTPException, Header, Depends
from sqlalchemy.orm import Session as DBSession

from app.config import settings
from app.db.base import get_db
from app.db import models


# ---- API key hashing (high-entropy keys → fast SHA-256, prefix for lookup/rotation UX) ----
def hash_api_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def key_prefix(raw: str) -> str:
    return raw[:8]


def _origin_host(origin: str | None) -> str:
    if not origin:
        return ""
    netloc = urlparse(origin).netloc or origin
    return netloc.lower()


def _host_allowed(host: str, domains: list[str]) -> bool:
    for d in domains:
        d = d.lower().strip()
        if d == host:
            return True
        if d.startswith("*.") and (host == d[2:] or host.endswith(d[1:])):
            return True
    return False


def authenticate_widget(widget_key: str, origin: str | None, db: DBSession) -> models.Tenant:
    """Validate the per-brokerage widget key (by hash) and that the Origin is allowlisted."""
    rec = (
        db.query(models.ApiKey)
        .filter_by(key_hash=hash_api_key(widget_key), status="active")
        .first()
    )
    if not rec:
        raise HTTPException(status_code=401, detail="Invalid widget key")
    tenant = db.get(models.Tenant, rec.tenant_id)
    if not tenant or not tenant.is_active:
        raise HTTPException(status_code=401, detail="Tenant inactive")
    host = _origin_host(origin)
    domains = [d.domain for d in db.query(models.DomainAllowlist).filter_by(tenant_id=tenant.id).all()]
    if host and domains and not _host_allowed(host, domains):
        raise HTTPException(status_code=403, detail=f"Origin '{host}' not allowlisted for this tenant")
    return tenant


def issue_session_token(tenant_id: int, session_id: str) -> str:
    now = int(time.time())
    payload = {"sub": session_id, "tid": tenant_id, "iat": now,
               "exp": now + settings.session_ttl_seconds}
    return jwt.encode(payload, settings.session_jwt_secret, algorithm="HS256")


def new_session_id() -> str:
    return uuid.uuid4().hex


def require_session(
    authorization: str | None = Header(None),
    db: DBSession = Depends(get_db),
) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing session token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.session_jwt_secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid session token")
    return {"session_id": payload["sub"], "tenant_id": payload["tid"], "db": db}
