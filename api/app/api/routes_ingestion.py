"""Phase 4 — admin-gated ingestion visibility + manual trigger.

Read endpoints expose source cadences and recent ``IngestionRun`` rows for the admin dashboard. The
trigger runs the orchestrator once (offline fixtures unless BA_INGEST_LIVE is set) and is audited. The
recurring schedule itself is a worker concern (never the web process), per P4-D3."""
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.config import settings
from app.core.admin_security import require_admin, audit
from app.core.ratelimit import client_ip
from app.db.base import get_db
from app.db import models
from app.ingestion.base import SOURCE_NAMES, get_source
from app.ingestion.orchestrator import ingest_all, ingest_source
from app.schemas.ingestion import SourceInfo, IngestRequest, IngestionRunOut

router = APIRouter(prefix="/api/v1/admin/ingestion", tags=["ingestion"])


@router.get("/sources", response_model=list[SourceInfo])
def list_sources(user: models.User = Depends(require_admin)):
    cadences = settings.ingest_cadences
    return [SourceInfo(name=n, mode=get_source(n).mode, cron=cadences[n]) for n in SOURCE_NAMES]


@router.get("/runs", response_model=list[IngestionRunOut])
def list_runs(user: models.User = Depends(require_admin), db: DBSession = Depends(get_db)):
    rows = db.query(models.IngestionRun).order_by(models.IngestionRun.id.desc()).limit(50).all()
    return [
        IngestionRunOut(
            id=r.id, source=r.source, mode=r.mode, status=r.status, discovered=r.discovered,
            registered=r.registered, versioned=r.versioned, duplicates=r.duplicates,
            chunks_written=r.chunks_written, errors=r.errors,
            started_at=r.started_at.isoformat() if r.started_at else None,
            finished_at=r.finished_at.isoformat() if r.finished_at else None,
        ) for r in rows
    ]


@router.post("/run")
def run_ingestion(body: IngestRequest, request: Request,
                  user: models.User = Depends(require_admin), db: DBSession = Depends(get_db)):
    if not body.all and not body.source:
        raise HTTPException(status_code=400, detail="specify 'source' or set 'all' true")
    if body.source and body.source not in SOURCE_NAMES:
        raise HTTPException(status_code=404, detail=f"unknown source; known: {list(SOURCE_NAMES)}")

    report = ingest_all(db, actor=user.email) if body.all else ingest_source(
        db, body.source, actor=user.email)
    audit(db, user.id, "ingest_run",
          target=("all" if body.all else body.source),
          detail={"chunks_written": report["chunks_written"], "errors": report["errors"]},
          ip=client_ip(request))
    return report
