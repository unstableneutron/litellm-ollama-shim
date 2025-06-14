"""LiteLLM proxy wrapper exposing Ollama compatible routes."""

from __future__ import annotations

import datetime as _dt
import json
import os
import uuid
from typing import Any, AsyncGenerator

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

import litellm
from litellm.proxy.proxy_server import app as _proxy_app


def build_app() -> FastAPI:
    """Return a FastAPI app with added Ollama style endpoints."""

    app: FastAPI = _proxy_app
    router = APIRouter()

    @router.get("/api/tags")
    async def tags() -> dict[str, Any]:
        models = []
        for m in getattr(app.state, "model_config", []):
            models.append(
                {
                    "name": getattr(m, "display_name", None) or getattr(m, "id", ""),
                    "model": getattr(m, "id", ""),
                    "modified_at": _dt.datetime.utcnow().isoformat() + "Z",
                    "size": 1,
                    "digest": uuid.uuid4().hex,
                    "details": {
                        "family": getattr(m, "family", None) or "custom",
                        "format": "proxy",
                        "parameter_size": str(getattr(m, "context_window", "")),
                    },
                }
            )
        return {"models": models}

    @router.post("/api/chat")
    async def chat(request: Request) -> Any:
        body = await request.json()
        stream = body.get("stream", False)

        async def litestream() -> AsyncGenerator[str, None]:
            gen = await litellm.acompletion(
                model=body["model"],
                messages=body["messages"],
                stream=True,
            )
            async for chunk in gen:
                content = chunk["choices"][0].get("delta", {}).get("content", "")
                payload = {"message": {"role": "assistant", "content": content}, "done": False}
                yield f"data: {json.dumps(payload)}\n\n"
            yield "data: {\"done\": true}\n\n"

        if stream:
            return StreamingResponse(litestream(), media_type="text/event-stream")

        completion = await litellm.acompletion(
            model=body["model"],
            messages=body["messages"],
        )
        content = completion["choices"][0]["message"]["content"]
        return {"message": {"role": "assistant", "content": content}}

    @router.get("/api/show")
    async def show(name: str) -> Any:
        tag_list = (await tags())["models"]
        for m in tag_list:
            if m["model"] == name:
                return m
        return JSONResponse(status_code=404, content={"error": "model not found"})

    app.include_router(router)
    return app


def main() -> None:  # pragma: no cover - entry point
    import uvicorn

    uvicorn.run(
        build_app(),
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "4000")),
    )

