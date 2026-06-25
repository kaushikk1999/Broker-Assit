"""Phase 6 Sarvam language adapter — detect/translate, code mapping, gating, graceful fallback."""
import pytest

from app.adapters import get_language
from app.adapters.mocks import MockLanguage
from app.adapters.sarvam_cloud import SarvamLanguage, _to_internal, _script_detect


def test_factory_is_mock_in_mocks_mode():
    assert isinstance(get_language(), MockLanguage)


def test_requires_api_key():
    with pytest.raises(RuntimeError):
        SarvamLanguage(api_key="")


def test_code_mapping_to_internal():
    assert _to_internal("hi-IN") == "hi"
    assert _to_internal("ta-IN") == "ta"
    assert _to_internal("en-IN") == "en"
    assert _to_internal("bn-IN") == "en"  # unsupported → en
    assert _to_internal("") == "en"


def test_script_fallback_detector():
    assert _script_detect("வணக்கம்") == "ta"
    assert _script_detect("नमस्ते") == "hi"
    assert _script_detect("hello") == "en"


def test_detect_uses_api(monkeypatch):
    s = SarvamLanguage(api_key="k")
    monkeypatch.setattr(s, "_post", lambda path, body: {"language_code": "ta-IN"})
    assert s.detect("எதோ ஒரு உரை") == "ta"


def test_detect_falls_back_to_script_on_error(monkeypatch):
    s = SarvamLanguage(api_key="k")
    monkeypatch.setattr(s, "_post", lambda path, body: (_ for _ in ()).throw(RuntimeError("down")))
    assert s.detect("नमस्ते दुनिया") == "hi"


def test_translate_uses_api_and_maps_codes(monkeypatch):
    s = SarvamLanguage(api_key="k")
    captured = {}

    def fake_post(path, body):
        captured.update(body)
        captured["path"] = path
        return {"translated_text": "अनुवादित"}

    monkeypatch.setattr(s, "_post", fake_post)
    out = s.translate("hello", target="hi", source="en")
    assert out == "अनुवादित"
    assert captured["path"] == "translate"
    assert captured["source_language_code"] == "en-IN"
    assert captured["target_language_code"] == "hi-IN"


def test_translate_noop_same_lang():
    s = SarvamLanguage(api_key="k")
    assert s.translate("hello", target="en", source="en") == "hello"


def test_translate_returns_original_on_error(monkeypatch):
    s = SarvamLanguage(api_key="k")
    monkeypatch.setattr(s, "_post", lambda path, body: (_ for _ in ()).throw(RuntimeError("down")))
    assert s.translate("keep me", target="hi", source="en") == "keep me"
