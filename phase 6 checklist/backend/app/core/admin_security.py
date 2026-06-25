"""Admin authentication plane: bcrypt passwords, admin JWT, login lockout, role dependencies."""
import time
from datetime import datetime, timedelta

import bcrypt
import jwt
from fastapi import HTTPException, Header, Depends
from sqlalchemy.orm import Session as DBSession

from app.config import settings
from app.db.base import get_db
from app.db import models


def hash_password(raw: str) -> str:
    return bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()


def verify_password(raw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(raw.encode(), hashed.encode())
    except ValueError:
        return False


def issue_admin_token(user: models.User) -> str:
    now = int(time.time())
    payload = {"sub": user.id, "role": user.role, "typ": "admin",
               "iat": now, "exp": now + settings.admin_jwt_ttl_seconds}
    return jwt.encode(payload, settings.admin_jwt_secret, algorithm="HS256")


def authenticate_admin(email: str, password: str, db: DBSession) -> models.User:
    """Verify credentials with lockout. Generic 401 on failure (no user-enumeration)."""
    user = db.query(models.User).filter_by(email=email.lower().strip()).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(status_code=423, detail="Account temporarily locked")
    if not verify_password(password, user.password_hash):
        user.failed_attempts += 1
        if user.failed_attempts >= settings.admin_max_failed_logins:
            user.locked_until = datetime.utcnow() + timedelta(seconds=settings.admin_lockout_seconds)
            user.failed_attempts = 0
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user.failed_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.utcnow()
    db.commit()
    return user


def require_admin(authorization: str | None = Header(None),
                  db: DBSession = Depends(get_db)) -> models.User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing admin token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.admin_jwt_secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Admin session expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid admin token")
    if payload.get("typ") != "admin":
        raise HTTPException(status_code=401, detail="Not an admin token")
    user = db.get(models.User, payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Admin not found")
    return user


def require_superadmin(user: models.User = Depends(require_admin)) -> models.User:
    if user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Superadmin required")
    return user


def audit(db: DBSession, user_id: int | None, action: str, target: str = "",
          detail: dict | None = None, ip: str = "") -> None:
    db.add(models.AdminAuditLog(user_id=user_id, action=action, target=target,
                                detail=detail or {}, ip=ip))
    db.commit()
