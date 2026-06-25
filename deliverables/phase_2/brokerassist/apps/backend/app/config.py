"""Central configuration. Mocks-first for AI; real Postgres/Redis/Qdrant/Ollama gated by env.

Phase 5 (Embedding Pipeline) adds embeddinggemma + Qdrant dual-vector settings. Canonical names follow
the roadmap/starter-pack (e.g. BA_QDRANT_COLLECTION_NAME=brokerage_kb, BA_OLLAMA_CLOUD_API_KEY); the
prior Phase-3 env names are kept as backward-compatible aliases via AliasChoices so nothing breaks."""
from pydantic import Field, AliasChoices
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

    # ---------------------------------------------------------------- Qdrant (vector store)
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    # Canonical collection name = brokerage_kb (roadmap). Legacy alias: BA_QDRANT_COLLECTION.
    qdrant_collection_name: str = Field(
        "brokerage_kb",
        validation_alias=AliasChoices("BA_QDRANT_COLLECTION_NAME", "BA_QDRANT_COLLECTION"),
    )
    # Dual-vector names for the brokerage_kb collection (named dense + native sparse).
    qdrant_dense_vector_name: str = "dense"
    qdrant_sparse_vector_name: str = "sparse"
    qdrant_validate_on_startup: bool = True
    # Collection creation is a STARTUP responsibility; OFF by default (validate-only). Opt-in to create.
    qdrant_create_collection_on_startup: bool = Field(
        False,
        validation_alias=AliasChoices("BA_QDRANT_CREATE_COLLECTION_ON_STARTUP", "BA_QDRANT_CREATE_IF_MISSING"),
    )

    # ---------------------------------------------------------------- Phase 5 — Embedding pipeline
    # Ollama Cloud (embeddinggemma). No local weights. Secrets injected via env; never defaulted.
    ollama_cloud_url: str = ""
    ollama_cloud_api_key: str = Field(
        "", validation_alias=AliasChoices("BA_OLLAMA_CLOUD_API_KEY", "BA_OLLAMA_API_KEY"),
    )
    embedding_model: str = "embeddinggemma"
    # Dimension is NEVER hardcoded — it is detected from a probe embedding. This optional override is a
    # validation assertion only. Legacy alias: BA_QDRANT_DENSE_DIM.
    embedding_dimension_override: int | None = Field(
        None, validation_alias=AliasChoices("BA_EMBEDDING_DIMENSION_OVERRIDE", "BA_QDRANT_DENSE_DIM"),
    )
    embedding_batch_size: int = 16
    embedding_concurrency: int = 2
    embedding_retry_count: int = 3
    embedding_timeout_seconds: int = 30
    # Fatal-error policy: when a REAL vendor is configured and validation fails, stop startup. In mocks
    # mode (no Qdrant/Ollama configured) startup always proceeds (credential-free invariant).
    ingestion_fail_fast: bool = True

    # Canonical metadata enums (CSV; parsed by the metadata contract).
    metadata_language_codes: str = "en,hi,ta"
    metadata_filing_types: str = (
        "Annual Report,Quarterly Results,Shareholding Pattern,Board Meeting,"
        "Corporate Action,Financial Results,Press Release,Presentation,FAQ"
    )
    # Chunking knobs (Phase 4 owns chunking; Phase 5 reads/validates against these bounds).
    chunk_size: int = 500
    chunk_overlap: int = 100

    @property
    def language_codes(self) -> list[str]:
        return [c.strip() for c in self.metadata_language_codes.split(",") if c.strip()]

    @property
    def filing_types(self) -> list[str]:
        return [c.strip() for c in self.metadata_filing_types.split(",") if c.strip()]

    @property
    def qdrant_configured(self) -> bool:
        return bool(self.qdrant_url)

    @property
    def ollama_configured(self) -> bool:
        return bool(self.ollama_cloud_url and self.ollama_cloud_api_key)


settings = Settings()
