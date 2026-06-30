"""Chat + analytics persistence (PostgreSQL). Keeps conversation history and an event stream."""
from sqlalchemy.orm import Session as DBSession

from app.db import models


def persist_turn(db: DBSession, tenant_id: int, session_id: str, user_msg: str,
                 answer: str, language: str, intent: str, branch: str) -> None:
    conv = (db.query(models.ChatConversation)
            .filter_by(tenant_id=tenant_id, session_id=session_id)
            .order_by(models.ChatConversation.id.desc()).first())
    if not conv:
        conv = models.ChatConversation(tenant_id=tenant_id, session_id=session_id)
        db.add(conv)
        db.flush()
    db.add(models.ChatMessage(conversation_id=conv.id, role="user", content=user_msg,
                              language=language, intent=intent, branch=branch))
    db.add(models.ChatMessage(conversation_id=conv.id, role="assistant", content=answer,
                              language=language, intent=intent, branch=branch))
    db.commit()


def log_event(db: DBSession, event_type: str, tenant_id: int | None = None,
              session_id: str | None = None, payload: dict | None = None) -> None:
    db.add(models.Analytics(event_type=event_type, tenant_id=tenant_id,
                            session_id=session_id, payload=payload or {}))
    db.commit()
