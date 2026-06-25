"""Health / readiness / liveness + minimal transparency endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session as DBSession

from app.db.base import get_db
from app.db import models
from app.config import settings
from app.core.redis import cache
from app.adapters.qdrant_real import qdrant_status

router = APIRouter(tags=["meta"])


@router.get("/health")
def health():
    return {"status": "ok", "use_mocks": settings.use_mocks, "env": settings.environment}


@router.get("/live")
def live():
    """Liveness: process is up (no dependency checks)."""
    return {"status": "alive"}


@router.get("/ready")
def ready(db: DBSession = Depends(get_db)):
    """Readiness: dependencies reachable."""
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
    deps = {
        "postgres": {"ok": db_ok},
        "redis": {"backend": cache.name, "ok": cache.ping()},
        "qdrant": qdrant_status(),
    }
    ready_ok = db_ok and deps["redis"]["ok"]
    return {
        "status": "ready" if ready_ok else "degraded",
        "tenants": db.query(models.Tenant).count() if db_ok else None,
        "documents": db.query(models.Document).count() if db_ok else None,
        "dependencies": deps,
    }


@router.get("/api/v1/admin/documents")
def list_documents(db: DBSession = Depends(get_db)):
    docs = db.query(models.Document).all()
    return [{"id": d.id, "source": d.source, "title": d.title, "url": d.url,
             "filing_type": d.filing_type,
             "filing_date": d.filing_date.isoformat() if d.filing_date else None} for d in docs]
