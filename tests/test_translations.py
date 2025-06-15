"""Tests for translation between LiteLLM and Ollama APIs."""

from fastapi.testclient import TestClient

import litellm_ollama_shim as shim
from litellm_ollama_shim import types
from litellm_ollama_shim.types import ChatRequest, TagsResponse


class DummyModel:
    """Minimal stub to simulate a LiteLLM model config."""

    def __init__(self, id, display_name=None, family=None, context_window=0):
        """Store attributes used by the shim during tests."""
        self.id = id
        self.display_name = display_name
        self.family = family
        self.context_window = context_window


def build_client(monkeypatch):
    """Return a TestClient with patched LiteLLM completion."""
    app = shim.build_app()
    app.state.model_config = [
        DummyModel("foo", display_name="Foo Model", family="llama", context_window=2048)
    ]

    async def fake_acompletion(**kwargs):
        if kwargs.get("stream"):

            async def gen():
                yield {"choices": [{"delta": {"content": "hi"}}]}
                yield {"choices": [{}]}

            return gen()
        return {"choices": [{"message": {"content": "hi"}}]}

    monkeypatch.setattr(shim.litellm, "acompletion", fake_acompletion)
    return TestClient(app)


def test_tags(monkeypatch):
    """`/api/tags` should return available models."""
    client = build_client(monkeypatch)
    resp = client.get("/api/tags")
    assert resp.status_code == 200
    data = TagsResponse.model_validate(resp.json())
    assert data.models[0].model == "foo"
    assert data.models[0].name == "Foo Model"


def test_chat(monkeypatch):
    """Non-streaming chat endpoint should return a full message."""
    client = build_client(monkeypatch)
    resp = client.post(
        "/api/chat",
        json=ChatRequest(
            model="foo", messages=[{"role": "user", "content": "?"}]
        ).model_dump(),
    )
    assert resp.status_code == 200
    assert resp.json()["message"]["content"] == "hi"


def test_chat_stream(monkeypatch):
    """Streaming chat endpoint should yield chunks."""
    client = build_client(monkeypatch)
    resp = client.post(
        "/api/chat",
        json=ChatRequest(
            model="foo", messages=[{"role": "user", "content": "?"}], stream=True
        ).model_dump(),
    )
    chunks = list(resp.iter_lines())
    assert any("data:" in c for c in chunks)
    assert 'data: {"done": true}' in chunks[-2]


def test_show(monkeypatch):
    """`/api/show` should look up a model by name."""
    client = build_client(monkeypatch)
    resp = client.get("/api/show", params={"name": "foo"})
    assert resp.status_code == 200
    data = types.Tag.model_validate(resp.json())
    assert data.model == "foo"
