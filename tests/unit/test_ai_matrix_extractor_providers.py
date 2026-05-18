"""Tests for vision_extractor.extract() — provider routing and error paths."""
import os
import json
import pytest

from pyarchinit_mini.ai_matrix.vision_extractor import extract


def test_extract_unknown_provider_raises():
    with pytest.raises(ValueError, match="unknown provider"):
        extract(b"fake bytes", None, "gemini")


def test_extract_oversized_image_rejected():
    big = b"x" * (11 * 1024 * 1024)  # 11MB
    r = extract(big, None, "anthropic")
    assert r.rejected is True
    assert "10MB" in r.reason or "troppo grande" in r.reason


def test_extract_anthropic_missing_key_raises(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        extract(b"\x89PNG\r\n\x1a\n" + b"x" * 100, None, "anthropic")


def test_extract_openai_missing_key_raises(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        extract(b"\x89PNG\r\n\x1a\n" + b"x" * 100, None, "openai")


def test_extract_anthropic_call_with_mock(monkeypatch):
    """End-to-end with mocked anthropic client."""
    fake_payload = json.dumps({
        "is_harris_matrix": True,
        "confidence": 0.9,
        "reason": "OK",
        "detected_site": "S1",
        "detected_area": None,
        "us": [{"us_num": "1", "area": "A", "unit_type": "US",
                "descrizione": "test", "fase_recente": 1, "fase_iniziale": 1}],
        "edges": [],
    })

    class FakeContent:
        def __init__(self, text): self.text = text
    class FakeResponse:
        content = [FakeContent(fake_payload)]
    class FakeMessages:
        def create(self, **kw): return FakeResponse()
    class FakeClient:
        def __init__(self, **kw): self.messages = FakeMessages()

    import anthropic
    monkeypatch.setattr(anthropic, "Anthropic", FakeClient)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    r = extract(b"\x89PNG\r\n\x1a\n" + b"x" * 100, "context text", "anthropic")
    assert r.rejected is False
    assert r.plan.detected_site == "S1"


def test_extract_openai_call_with_mock(monkeypatch):
    """End-to-end with mocked openai client."""
    fake_payload = json.dumps({
        "is_harris_matrix": True,
        "confidence": 0.85,
        "reason": "OK",
        "detected_site": "S2",
        "detected_area": "Area east",
        "us": [{"us_num": "5", "area": "Area east", "unit_type": "USR",
                "descrizione": "intonaco", "fase_recente": 2, "fase_iniziale": 2}],
        "edges": [],
    })

    class FakeMessage:
        def __init__(self, content): self.content = content
    class FakeChoice:
        def __init__(self, content): self.message = FakeMessage(content)
    class FakeCompletion:
        def __init__(self, content): self.choices = [FakeChoice(content)]
    class FakeCompletions:
        def create(self, **kw): return FakeCompletion(fake_payload)
    class FakeChat:
        def __init__(self): self.completions = FakeCompletions()
    class FakeClient:
        def __init__(self, **kw): self.chat = FakeChat()

    import openai
    monkeypatch.setattr(openai, "OpenAI", FakeClient)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    r = extract(b"\x89PNG\r\n\x1a\n" + b"x" * 100, "hint", "openai")
    assert r.rejected is False
    assert r.plan.detected_site == "S2"
    assert r.plan.us[0].unit_type == "USR"
