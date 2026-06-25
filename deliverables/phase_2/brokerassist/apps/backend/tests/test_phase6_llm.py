"""Phase 6 Gemma generation (Ollama Cloud) — grounded prompt, response parsing, gating."""
import pytest

from app.adapters import get_llm
from app.adapters.mocks import MockLLM
from app.adapters.ollama_cloud import OllamaCloudLLM, build_grounded_prompt, _extract_text


def test_factory_is_mock_in_mocks_mode():
    assert isinstance(get_llm(), MockLLM)


def test_requires_config():
    with pytest.raises(RuntimeError):
        OllamaCloudLLM(base_url="", api_key="")


def test_grounded_prompt_numbers_context_and_forbids_guessing():
    system, user = build_grounded_prompt("What did NALCO report?", ["revenue rose", "dividend declared"])
    assert "ONLY" in system and "not investment advice" in system.lower()
    assert "[1] revenue rose" in user and "[2] dividend declared" in user
    assert "What did NALCO report?" in user


def test_grounded_prompt_handles_empty_context():
    _system, user = build_grounded_prompt("q", [])
    assert "(no context)" in user


def test_extract_text_chat_and_generate_shapes():
    assert _extract_text({"message": {"role": "assistant", "content": "  hi there  "}}) == "hi there"
    assert _extract_text({"response": "fallback text"}) == "fallback text"


def test_extract_text_raises_on_empty():
    with pytest.raises(RuntimeError):
        _extract_text({"foo": "bar"})


def test_generate_uses_post(monkeypatch):
    llm = OllamaCloudLLM(base_url="https://ollama.example", api_key="k", model="gemma2")
    captured = {}

    def fake_post(system, user):
        captured["system"], captured["user"] = system, user
        return "NALCO reported higher revenue."

    monkeypatch.setattr(llm, "_post", fake_post)
    out = llm.generate("What did NALCO report?", ["NALCO revenue rose this quarter"])
    assert out == "NALCO reported higher revenue."
    assert "[1] NALCO revenue rose this quarter" in captured["user"]
