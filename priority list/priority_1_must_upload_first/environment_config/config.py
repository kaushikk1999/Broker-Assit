"""Central configuration. Mocks-first for AI; real Postgres/Redis/Qdrant gated by env (Phase 3)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="BA_", extra="ignore")

    app_name: str = "BrokerAssist API"
    environment: str = "local"

    # Mocks-first switch for AI providers (Ollama gen/embeddings, Sarvam, re-ranker).
    use_mocks: bool = True

    # Market-data provider selector (roadmap Source 2A). "mock" keeps the deterministic mock even when
    # use_mocks=False, so market stays safe until a real TrueData/Ticker adapter is wired. Referenced by
    # adapters.get_marketdata(); env var BA_MARKETDATA_PROVIDER.
    marketdata_provider: str = "mock"

    # Storage. SQLite by default; set postgresql://... for Railway/production.
    database_url: str = "sqlite:///./brokerassist.db"
    # Redis (session cache, chat context, rate-limit/quota counters). Empty => in-memory fallback.
    redis_url: str = ""

    # Security — sessions (anonymous widget visitors)
    session_jwt_secret: str = "dev-only-change-me"
    session_ttl_seconds: int = 1800
    # Security — admin plane
    admin_jwt_secret: str = "dev-only-change-me-admin"
    admin_jwt_ttl_seconds: int = 3600
    admin_max_failed_logins: int = 5
    admin_lockout_seconds: int = 900

    # Abuse & cost control (roadmap Phase 3)
    rate_limit_per_session_per_min: int = 20
    rate_limit_sessions_per_ip_per_hour: int = 60
    rate_limit_per_ip_per_min: int = 40
    tenant_daily_quota: int = 5000

    # RAG pipeline tunables (used by reused services)
    retrieve_top_k: int = 20
    rerank_top_k: int = 5

    supported_languages: tuple[str, ...] = ("en", "hi", "ta")

    # --- Phase 3 external infra (validation/connectivity only this phase) ---
    # Qdrant: real connectivity + startup collection validation (NO ingestion/embeddings here).
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    qdrant_collection: str = "brokerassist_knowledge"
    # Dense vector dimension is NOT hardcoded; provided by config and only *validated* this phase.
    qdrant_dense_dim: int | None = None
    qdrant_validate_on_startup: bool = True
    qdrant_create_if_missing: bool = False  # Phase 3 default: validate, don't create

    # Ollama key is stored ONLY (embeddings/generation are Phase 5/6, out of Phase 3 scope).
    ollama_api_key: str = ""


settings = Settings()
