"""Central configuration. Mocks-first for AI; real Postgres/Redis/Qdrant/Ollama gated by env.

Phase 5 (Embedding Pipeline) adds embeddinggemma + Qdrant dual-vector settings. Canonical names follow
the roadmap/starter-pack (e.g. BA_QDRANT_COLLECTION_NAME=brokerage_kb, BA_OLLAMA_CLOUD_API_KEY); the
prior Phase-3 env names are kept as backward-compatible aliases via AliasChoices so nothing breaks."""
import os

from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

# Local dev convenience: load a `.env` file. Production injects env vars directly (no file). Tests set
# BA_DISABLE_DOTENV=1 so a filled-in local `.env` (real vendor creds) can't flip the suite off the
# mocks-first path or shadow the config-default assertions.
_ENV_FILE = None if os.environ.get("BA_DISABLE_DOTENV") else ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, env_prefix="BA_", extra="ignore")

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

    # ---------------------------------------------------------------- Phase 6 — RAG System knobs
    # Reciprocal Rank Fusion constant (k in 1/(k+rank)); 60 is the de-facto default.
    rrf_k: int = 60
    # Deterministic, provider-agnostic query expansion before embedding (improves recall).
    query_expansion_enabled: bool = True
    # When the hosted reranker is unreachable, degrade gracefully to the incoming RRF order.
    rerank_fallback_enabled: bool = True
    # Apply a language metadata filter at retrieval. OFF by default: the query is translated to English
    # and embeddinggemma is multilingual, so filtering by user language would wrongly exclude EN docs.
    retrieval_language_filter: bool = False

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
    # Embedding provider selector (like marketdata_provider). "auto" = real Ollama Cloud when
    # configured + not use_mocks, else mock. "mock" forces the deterministic mock even when use_mocks is
    # off — needed because Ollama Cloud hosts NO embedding models, so dense embeddings have no live
    # provider yet while generation/translation/Qdrant run for real. "ollama" forces the real adapter.
    embedding_provider: str = "auto"  # auto | mock | ollama
    # Dimension is NEVER hardcoded — it is detected from a probe embedding. This optional override is a
    # validation assertion only. Legacy alias: BA_QDRANT_DENSE_DIM.
    embedding_dimension_override: int | None = Field(
        None, validation_alias=AliasChoices("BA_EMBEDDING_DIMENSION_OVERRIDE", "BA_QDRANT_DENSE_DIM"),
    )
    embedding_batch_size: int = 16
    embedding_concurrency: int = 2
    embedding_retry_count: int = 3
    embedding_timeout_seconds: int = 30

    # ---------------------------------------------------------------- Phase 6 — generation (Gemma)
    # Reuses ollama_cloud_url + ollama_cloud_api_key (same hosted Ollama Cloud account as embeddings).
    # No local weights run in-process. Secrets are injected via env; never defaulted.
    ollama_gen_model: str = Field(
        "gemma2", validation_alias=AliasChoices("BA_OLLAMA_GEN_MODEL", "BA_GEN_MODEL"),
    )
    gen_timeout_seconds: int = 60
    gen_retry_count: int = 2
    gen_max_tokens: int = 700
    gen_temperature: float = 0.2

    # ---------------------------------------------------------------- Phase 6 — hosted cross-encoder
    # Hosted re-ranker endpoint (e.g. BAAI/bge-reranker). No reranker weights run in-process.
    reranker_url: str = ""
    reranker_api_key: str = ""
    reranker_model: str = "BAAI/bge-reranker-base"
    reranker_timeout_seconds: int = 20
    reranker_retry_count: int = 2

    # ---------------------------------------------------------------- Phase 6/7 — Sarvam language
    # Real Sarvam detect/translate adapter (pulled into Phase 6). Credential-gated; mock otherwise.
    sarvam_base_url: str = "https://api.sarvam.ai"
    sarvam_api_key: str = Field(
        "", validation_alias=AliasChoices("BA_SARVAM_API_KEY", "BA_SARVAM_SUBSCRIPTION_KEY"),
    )
    sarvam_timeout_seconds: int = 20
    sarvam_retry_count: int = 2
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

    # ---------------------------------------------------------------- Phase 4 — Data Ingestion Layer
    # Master switch for LIVE source adapters (real crawl / NSE / BSE / NALCO IR / Google Drive). OFF by
    # default so the full pipeline runs on deterministic offline fixtures — credential- and network-free
    # (mocks-first invariant). When false, the live adapters refuse to fetch.
    ingest_live: bool = False
    # Per-source endpoints (only used when ingest_live=true). Empty => that live source is unconfigured.
    broker_site_url: str = ""
    nse_base_url: str = "https://www.nseindia.com"
    bse_base_url: str = "https://www.bseindia.com"
    nalco_ir_url: str = "https://nalcoindia.com"
    gdrive_folder_id: str = ""
    gdrive_credentials_json: str = ""
    # Refresh cadences (cron) wired in the Railway WORKER only — never the web process (P4-D3). The
    # scheduler abstraction parses these; run-once commands ignore them. Defaults mirror roadmap p. 31.
    ingest_cron_broker: str = "0 2 * * *"     # Broker website — daily @ 02:00
    ingest_cron_nse: str = "0 * * * *"        # NSE corporate filings — hourly
    ingest_cron_bse: str = "0 * * * *"        # BSE — hourly
    ingest_cron_nalco: str = "0 3 * * *"      # NALCO IR — daily @ 03:00
    ingest_cron_gdrive: str = "*/15 * * * *"  # Google Drive — every 15 minutes

    @property
    def language_codes(self) -> list[str]:
        return [c.strip() for c in self.metadata_language_codes.split(",") if c.strip()]

    @property
    def filing_types(self) -> list[str]:
        return [c.strip() for c in self.metadata_filing_types.split(",") if c.strip()]

    @property
    def ingest_cadences(self) -> dict[str, str]:
        """Source -> cron cadence map (roadmap refresh schedule). Consumed by the worker scheduler."""
        return {
            "broker_site": self.ingest_cron_broker,
            "nse": self.ingest_cron_nse,
            "bse": self.ingest_cron_bse,
            "nalco_ir": self.ingest_cron_nalco,
            "gdrive": self.ingest_cron_gdrive,
        }

    @property
    def qdrant_configured(self) -> bool:
        return bool(self.qdrant_url)

    @property
    def ollama_configured(self) -> bool:
        return bool(self.ollama_cloud_url and self.ollama_cloud_api_key)

    @property
    def generation_configured(self) -> bool:
        """Real Gemma generation (Ollama Cloud) is reachable. Shares the embedding credentials."""
        return bool(self.ollama_cloud_url and self.ollama_cloud_api_key and self.ollama_gen_model)

    @property
    def reranker_configured(self) -> bool:
        """Hosted cross-encoder re-ranker endpoint is configured."""
        return bool(self.reranker_url)

    @property
    def sarvam_configured(self) -> bool:
        """Real Sarvam language (detect/translate) adapter is configured."""
        return bool(self.sarvam_api_key)


settings = Settings()
