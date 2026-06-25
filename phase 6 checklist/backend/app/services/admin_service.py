"""Admin helpers: API-key generation (raw shown once), rotation/revocation."""
import secrets
from datetime import datetime

from sqlalchemy.orm import Session as DBSession

from app.core.security import hash_api_key, key_prefix
from app.db import models


def generate_api_key() -> str:
    return "ba_" + secrets.token_urlsafe(24)


def create_api_key(db: DBSession, tenant_id: int) -> tuple[str, models.ApiKey]:
    raw = generate_api_key()
    rec = models.ApiKey(tenant_id=tenant_id, key_prefix=key_prefix(raw),
                        key_hash=hash_api_key(raw), status="active")
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return raw, rec


def revoke_api_key(db: DBSession, key_id: int) -> models.ApiKey | None:
    rec = db.get(models.ApiKey, key_id)
    if rec and rec.status == "active":
        rec.status = "revoked"
        rec.revoked_at = datetime.utcnow()
        db.commit()
    return rec
