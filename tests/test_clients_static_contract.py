import pytest

from uss_engine.clients import ClientConfig, LLMClient, StaticLLMClient


def test_static_client_satisfies_llm_client_contract():
    client = StaticLLMClient(outputs=["artifact"])
    assert isinstance(client, LLMClient)
    assert client.complete([{"role": "user", "content": "Generate"}]) == "artifact"


def test_static_client_fails_when_empty():
    client = StaticLLMClient(outputs=[])
    with pytest.raises(RuntimeError):
        client.complete([])


def test_client_config_requires_model():
    with pytest.raises(ValueError):
        ClientConfig(model="")

from uss_engine.clients import AnthropicClient, OllamaClient, OpenAIClient
from uss_engine.clients.base import ClientConfig
from uss_engine.clients import openai_client, anthropic_client, ollama_client


def test_openai_client_payload_contract(monkeypatch):
    captured = {}

    def fake_post_json(*, url, payload, headers, timeout_seconds):
        captured.update({"url": url, "payload": payload, "headers": headers, "timeout": timeout_seconds})
        return {"choices": [{"message": {"content": "ok"}}]}

    monkeypatch.setattr(openai_client, "post_json", fake_post_json)
    client = OpenAIClient(ClientConfig(model="test-model", api_key="sk-test", base_url="https://example.test/v1"))
    assert client.complete([{"role": "user", "content": "hello"}]) == "ok"
    assert captured["url"] == "https://example.test/v1/chat/completions"
    assert captured["payload"]["model"] == "test-model"
    assert captured["payload"]["messages"] == [{"role": "user", "content": "hello"}]
    assert captured["headers"]["Authorization"] == "Bearer sk-test"


def test_anthropic_client_payload_contract(monkeypatch):
    captured = {}

    def fake_post_json(*, url, payload, headers, timeout_seconds):
        captured.update({"url": url, "payload": payload, "headers": headers, "timeout": timeout_seconds})
        return {"content": [{"type": "text", "text": "ok"}]}

    monkeypatch.setattr(anthropic_client, "post_json", fake_post_json)
    client = AnthropicClient(
        ClientConfig(model="claude-test", api_key="ak-test", base_url="https://example.test/v1"),
        max_tokens=123,
    )
    assert client.complete([
        {"role": "system", "content": "system rules"},
        {"role": "user", "content": "hello"},
    ]) == "ok"
    assert captured["url"] == "https://example.test/v1/messages"
    assert captured["payload"]["model"] == "claude-test"
    assert captured["payload"]["max_tokens"] == 123
    assert captured["payload"]["system"] == "system rules"
    assert captured["payload"]["messages"] == [{"role": "user", "content": "hello"}]
    assert captured["headers"]["x-api-key"] == "ak-test"
    assert "anthropic-version" in captured["headers"]


def test_ollama_client_payload_contract(monkeypatch):
    captured = {}

    def fake_post_json(*, url, payload, headers, timeout_seconds):
        captured.update({"url": url, "payload": payload, "headers": headers, "timeout": timeout_seconds})
        return {"message": {"content": "ok"}}

    monkeypatch.setattr(ollama_client, "post_json", fake_post_json)
    client = OllamaClient(ClientConfig(model="llama-test", base_url="http://localhost:11434"))
    assert client.complete([{"role": "user", "content": "hello"}]) == "ok"
    assert captured["url"] == "http://localhost:11434/api/chat"
    assert captured["payload"]["model"] == "llama-test"
    assert captured["payload"]["messages"] == [{"role": "user", "content": "hello"}]
    assert captured["payload"]["stream"] is False

from uss_engine.clients import GeminiClient, GrokClient
from uss_engine.clients import gemini_client, grok_client


def test_gemini_client_payload_contract(monkeypatch):
    captured = {}

    def fake_post_json(*, url, payload, headers, timeout_seconds):
        captured.update({"url": url, "payload": payload, "headers": headers, "timeout": timeout_seconds})
        return {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}

    monkeypatch.setattr(gemini_client, "post_json", fake_post_json)
    client = GeminiClient(ClientConfig(model="gemini-test", api_key="gm-test", base_url="https://example.test/v1beta"))
    assert client.complete([
        {"role": "system", "content": "system rules"},
        {"role": "user", "content": "hello"},
    ]) == "ok"
    assert captured["url"] == "https://example.test/v1beta/models/gemini-test:generateContent?key=gm-test"
    assert captured["payload"]["generationConfig"]["temperature"] == 0
    assert captured["payload"]["contents"][0]["role"] == "user"
    assert "SYSTEM INSTRUCTIONS" in captured["payload"]["contents"][0]["parts"][0]["text"]


def test_grok_client_payload_contract(monkeypatch):
    captured = {}

    def fake_post_json(*, url, payload, headers, timeout_seconds):
        captured.update({"url": url, "payload": payload, "headers": headers, "timeout": timeout_seconds})
        return {"choices": [{"message": {"content": "ok"}}]}

    monkeypatch.setattr(grok_client, "post_json", fake_post_json)
    client = GrokClient(ClientConfig(model="grok-test", api_key="xai-test", base_url="https://example.test/v1"))
    assert client.complete([{"role": "user", "content": "hello"}]) == "ok"
    assert captured["url"] == "https://example.test/v1/chat/completions"
    assert captured["payload"]["model"] == "grok-test"
    assert captured["payload"]["messages"] == [{"role": "user", "content": "hello"}]
    assert captured["headers"]["Authorization"] == "Bearer xai-test"
