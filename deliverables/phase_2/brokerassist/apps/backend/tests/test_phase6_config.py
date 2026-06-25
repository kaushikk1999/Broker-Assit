"""Phase 6 config: credential-free defaults and vendor-gating properties.

Mocks-first invariant: with no secrets set, every real-vendor *_configured property must be False so
the factories fall back to mocks. RAG knobs must carry sane defaults."""
from app.config import Settings


def _fresh(**env) -> Settings:
    """Build a Settings instance with an explicit env mapping (ignores process env via _env_file=None)."""
    return Settings(_env_file=None, **env)


def test_rag_knob_defaults():
    s = _fresh()
    assert s.rrf_k == 60
    assert s.query_expansion_enabled is True
    assert s.rerank_fallback_enabled is True
    assert s.retrieval_language_filter is False
    assert s.retrieve_top_k == 20 and s.rerank_top_k == 5


def test_vendor_configured_props_false_without_secrets():
    s = _fresh()
    assert s.reranker_configured is False
    assert s.sarvam_configured is False
    assert s.generation_configured is False
    # embedding/qdrant also unconfigured by default
    assert s.ollama_configured is False
    assert s.qdrant_configured is False


def test_generation_configured_requires_ollama_creds_and_model():
    # ollama_cloud_api_key + gen model bind via their canonical aliases (as env provides them).
    s = _fresh(ollama_cloud_url="https://ollama.example",
               BA_OLLAMA_CLOUD_API_KEY="k", BA_OLLAMA_GEN_MODEL="gemma2")
    assert s.generation_configured is True
    assert s.ollama_gen_model == "gemma2"


def test_reranker_configured_requires_url():
    s = _fresh(reranker_url="https://rerank.example/score")
    assert s.reranker_configured is True


def test_sarvam_configured_requires_key():
    s = _fresh(BA_SARVAM_API_KEY="sk-sarvam")
    assert s.sarvam_configured is True
    assert s.sarvam_base_url.startswith("https://")


def test_gen_model_alias():
    s = _fresh(BA_GEN_MODEL="gemma2:9b")
    assert s.ollama_gen_model == "gemma2:9b"
