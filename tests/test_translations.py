from fastapi.testclient import TestClient

import litellm_ollama_shim as shim
from litellm_ollama_shim import types
from litellm_ollama_shim.types import ChatRequest, TagsResponse

class DummyModel:
    def __init__(self, id, display_name=None, family=None, context_window=0):
        self.id = id
        self.display_name = display_name
        self.family = family
        self.context_window = context_window

def build_client(monkeypatch):
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
    client = build_client(monkeypatch)
    resp = client.get("/api/tags")
    assert resp.status_code == 200
    data = TagsResponse.model_validate(resp.json())
    assert data.models[0].model == "foo"
    assert data.models[0].name == "Foo Model"

def test_chat(monkeypatch):
    client = build_client(monkeypatch)
    resp = client.post(
        "/api/chat",
        json=ChatRequest(model="foo", messages=[{"role": "user", "content": "?"}]).model_dump(),
    )
    assert resp.status_code == 200
    assert resp.json()["message"]["content"] == "hi"


def test_chat_stream(monkeypatch):
    client = build_client(monkeypatch)
    resp = client.post(
        "/api/chat",
        json=ChatRequest(model="foo", messages=[{"role": "user", "content": "?"}], stream=True).model_dump(),
    )
    chunks = list(resp.iter_lines())
    assert any("data:" in c for c in chunks)
    assert "data: {\"done\": true}" in chunks[-2]


def test_show(monkeypatch):
    client = build_client(monkeypatch)
    resp = client.get("/api/show", params={"name": "foo"})
    assert resp.status_code == 200
    data = types.Tag.model_validate(resp.json())
    assert data.model == "foo"
