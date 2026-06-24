"""Admin plane: login + dashboard/management endpoints. Every write is audited."""
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.db.base import get_db
from app.db import models
from app.core.ratelimit import client_ip
from app.core.admin_security import (
    authenticate_admin, issue_admin_token, require_admin, require_superadmin, audit,
)
from app.services.admin_service import create_api_key, revoke_api_key
from app.config import settings
from app.schemas.admin import (
    AdminLogin, AdminToken, AdminMe, TenantCreate, TenantOut, ApiKeyOut, ApiKeyCreated,
    DomainIn, QuotaUpdate,
)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.post("/login", response_model=AdminToken)
def login(body: AdminLogin, request: Request, db: DBSession = Depends(get_db)):
    user = authenticate_admin(body.email, body.password, db)
    audit(db, user.id, "login", ip=client_ip(request))
    return AdminToken(admin_token=issue_admin_token(user),
                      expires_in=settings.admin_jwt_ttl_seconds, role=user.role)


@router.get("/me", response_model=AdminMe)
def me(user: models.User = Depends(require_admin)):
    return AdminMe(email=user.email, role=user.role)


# ---- tenants ----
@router.get("/tenants", response_model=list[TenantOut])
def list_tenants(user: models.User = Depends(require_admin), db: DBSession = Depends(get_db)):
    return [TenantOut(id=t.id, name=t.name, daily_quota=t.daily_quota, is_active=t.is_active)
            for t in db.query(models.Tenant).all()]


@router.post("/tenants", response_model=TenantOut)
def create_tenant(body: TenantCreate, request: Request,
                  user: models.User = Depends(require_superadmin), db: DBSession = Depends(get_db)):
    t = models.Tenant(name=body.name, daily_quota=body.daily_quota)
    db.add(t); db.commit(); db.refresh(t)
    audit(db, user.id, "create_tenant", target=str(t.id), detail={"name": t.name}, ip=client_ip(request))
    return TenantOut(id=t.id, name=t.name, daily_quota=t.daily_quota, is_active=t.is_active)


# ---- api keys ----
@router.get("/tenants/{tenant_id}/api-keys", response_model=list[ApiKeyOut])
def list_keys(tenant_id: int, user: models.User = Depends(require_admin), db: DBSession = Depends(get_db)):
    keys = db.query(models.ApiKey).filter_by(tenant_id=tenant_id).all()
    return [ApiKeyOut(id=k.id, key_prefix=k.key_prefix, status=k.status) for k in keys]


@router.post("/tenants/{tenant_id}/api-keys", response_model=ApiKeyCreated)
def create_key(tenant_id: int, request: Request,
               user: models.User = Depends(require_admin), db: DBSession = Depends(get_db)):
    if not db.get(models.Tenant, tenant_id):
        raise HTTPException(status_code=404, detail="Tenant not found")
    raw, rec = create_api_key(db, tenant_id)
    audit(db, user.id, "create_api_key", target=str(rec.id), detail={"tenant_id": tenant_id},
          ip=client_ip(request))
    return ApiKeyCreated(id=rec.id, key_prefix=rec.key_prefix, api_key=raw)


@router.post("/api-keys/{key_id}/revoke")
def revoke_key(key_id: int, request: Request,
               user: models.User = Depends(require_admin), db: DBSession = Depends(get_db)):
    rec = revoke_api_key(db, key_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Key not found")
    audit(db, user.id, "revoke_api_key", target=str(key_id), ip=client_ip(request))
    return {"id": key_id, "status": rec.status}


# ---- allowlist ----
@router.get("/tenants/{tenant_id}/allowlist")
def list_allowlist(tenant_id: int, user: models.User = Depends(require_admin),
                   db: DBSession = Depends(get_db)):
    return [{"id": d.id, "domain": d.domain}
            for d in db.query(models.DomainAllowlist).filter_by(tenant_id=tenant_id).all()]


@router.post("/tenants/{tenant_id}/allowlist")
def add_domain(tenant_id: int, body: DomainIn, request: Request,
               user: models.User = Depends(require_admin), db: DBSession = Depends(get_db)):
    d = models.DomainAllowlist(tenant_id=tenant_id, domain=body.domain.lower().strip())
    db.add(d); db.commit(); db.refresh(d)
    audit(db, user.id, "add_domain", target=str(tenant_id), detail={"domain": d.domain},
          ip=client_ip(request))
    return {"id": d.id, "domain": d.domain}


@router.delete("/allowlist/{domain_id}")
def remove_domain(domain_id: int, request: Request,
                  user: models.User = Depends(require_admin), db: DBSession = Depends(get_db)):
    d = db.get(models.DomainAllowlist, domain_id)
    if not d:
        raise HTTPException(status_code=404, detail="Domain not found")
    db.delete(d); db.commit()
    audit(db, user.id, "remove_domain", target=str(domain_id), ip=client_ip(request))
    return {"id": domain_id, "deleted": True}


# ---- quotas ----
@router.get("/tenants/{tenant_id}/quota")
def get_quota(tenant_id: int, user: models.User = Depends(require_admin), db: DBSession = Depends(get_db)):
    from datetime import date
    t = db.get(models.Tenant, tenant_id)
    if not t:
        raise HTTPException(status_code=404, detail="Tenant not found")
    row = db.query(models.UsageQuota).filter_by(tenant_id=tenant_id, day=date.today()).first()
    return {"tenant_id": tenant_id, "daily_quota": t.daily_quota, "used_today": row.count if row else 0}


@router.put("/tenants/{tenant_id}/quota")
def update_quota(tenant_id: int, body: QuotaUpdate, request: Request,
                 user: models.User = Depends(require_admin), db: DBSession = Depends(get_db)):
    t = db.get(models.Tenant, tenant_id)
    if not t:
        raise HTTPException(status_code=404, detail="Tenant not found")
    t.daily_quota = body.daily_quota; db.commit()
    audit(db, user.id, "update_quota", target=str(tenant_id), detail={"daily_quota": body.daily_quota},
          ip=client_ip(request))
    return {"tenant_id": tenant_id, "daily_quota": t.daily_quota}


# ---- security visibility ----
@router.get("/abuse")
def list_abuse(user: models.User = Depends(require_admin), db: DBSession = Depends(get_db)):
    rows = db.query(models.AbuseEvent).order_by(models.AbuseEvent.id.desc()).limit(50).all()
    return [{"id": r.id, "kind": r.kind, "ip": r.ip, "tenant_id": r.tenant_id,
             "detail": r.detail, "at": r.created_at.isoformat()} for r in rows]


@router.get("/audit")
def list_audit(user: models.User = Depends(require_admin), db: DBSession = Depends(get_db)):
    rows = db.query(models.AdminAuditLog).order_by(models.AdminAuditLog.id.desc()).limit(50).all()
    return [{"id": r.id, "user_id": r.user_id, "action": r.action, "target": r.target,
             "at": r.created_at.isoformat()} for r in rows]
