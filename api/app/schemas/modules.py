"""Request schemas for the discrete module endpoints (Search / Filings / Stock)."""
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    language: str | None = None


class FilingsRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    company: str | None = Field(None, description="Optional company filter, e.g. NALCO")
    language: str | None = None


class StockRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20)
    language: str | None = None
