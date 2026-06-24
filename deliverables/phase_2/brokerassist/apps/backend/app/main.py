"""BrokerAssist FastAPI app — Phase 3 backend foundation (mocks-first AI; real Postgres/Redis/Qdrant)."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.seed import seed
from app.core.observability import configure_logging, CorrelationIdMiddleware, log
from app.adapters.qdrant_real import validate_collection
from app.api import routes_chat, routes_meta, routes_admin, routes_modules


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    seed()  # create tables + seed demo tenant/api-key/allowlist, admin user, NALCO KB (idempotent)
    if settings.qdrant_validate_on_startup:
        status = validate_collection()
        log.info("qdrant startup validation: %s", status)
    yield


app = FastAPI(title=settings.app_name, version="0.3.0", lifespan=lifespan,
              description="Phase 3 — auth/access control, persistence, abuse control, module APIs.")

app.add_middleware(CorrelationIdMiddleware)
# Widget embeds cross-origin; CORS permissive at the edge (Origin allowlist enforced at /session).
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"], allow_credentials=False)

app.include_router(routes_meta.router)
app.include_router(routes_chat.router)
app.include_router(routes_modules.router)
app.include_router(routes_admin.router)


@app.get("/")
def root():
    return {"service": settings.app_name, "version": "0.3.0", "docs": "/docs",
            "endpoints": ["/health", "/ready", "/live", "/api/v1/session", "/api/v1/chat",
                          "/api/v1/search", "/api/v1/filings", "/api/v1/stock",
                          "/api/v1/admin/login", "/api/v1/admin/..."]}
