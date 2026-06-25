"""API contracts (OpenAPI is generated from these)."""
from pydantic import BaseModel, Field


class SessionRequest(BaseModel):
    widget_key: str = Field(..., description="Public per-brokerage widget key (tenant id)")


class SessionResponse(BaseModel):
    session_token: str
    expires_in: int


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    language: str | None = Field(None, description="User language hint: en|hi|ta. Auto-detected if omitted.")


class Citation(BaseModel):
    document_id: int
    chunk_id: int
    source: str
    title: str
    url: str
    filing_date: str | None = None


class ChatResponse(BaseModel):
    answer: str
    language: str
    intent: str
    branch: str  # "market" | "knowledge"
    citations: list[Citation] = []
    disclaimer: str
    debug: dict | None = None
