"""Admin plane schemas."""
from pydantic import BaseModel, Field


class AdminLogin(BaseModel):
    email: str
    password: str


class AdminToken(BaseModel):
    admin_token: str
    expires_in: int
    role: str


class AdminMe(BaseModel):
    email: str
    role: str


class TenantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    daily_quota: int = Field(5000, ge=0)


class TenantOut(BaseModel):
    id: int
    name: str
    daily_quota: int
    is_active: bool


class ApiKeyOut(BaseModel):
    id: int
    key_prefix: str
    status: str


class ApiKeyCreated(BaseModel):
    id: int
    key_prefix: str
    api_key: str  # shown ONCE on creation, never stored or returned again


class DomainIn(BaseModel):
    domain: str = Field(..., min_length=1, max_length=255)


class QuotaUpdate(BaseModel):
    daily_quota: int = Field(..., ge=0)
