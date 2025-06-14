"""LiteLLM proxy wrapper exposing Ollama compatible routes."""

from __future__ import annotations

import datetime as _dt
import json
import os
import uuid
from typing import Any, AsyncGenerator

from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse

import litellm
from litellm.proxy.proxy_server import app as _proxy_app

from .types import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ModelInfo,
    TagDetails,
    TagsResponse,
)


def build_app() -> FastAPI:
    """Return a FastAPI app with added Ollama style endpoints."""

    app: FastAPI = _proxy_app
    router = APIRouter()

    @router.get("/api/tags", response_model=TagsResponse)
    async def tags() -> TagsResponse:
        models = []
        for m in getattr(app.state, "model_config", []):
            models.append(
                ModelInfo(
                    name=getattr(m, "display_name", None) or getattr(m, "id", ""),
                    model=getattr(m, "id", ""),
                    modified_at=_dt.datetime.utcnow(),
                    size=1,
                    digest=uuid.uuid4().hex,
                    details=TagDetails(
                        family=getattr(m, "family", None) or "custom",
                        format="proxy",
                        parameter_size=str(getattr(m, "context_window", "")),
                    ),
                )
            )
        return TagsResponse(models=models)

    @router.post("/api/chat", response_model=ChatResponse)
    async def chat(request: Request) -> Any:
        body = ChatRequest(**await request.json())
        stream = bool(body.stream)

        async def litestream() -> AsyncGenerator[str, None]:
            gen = await litellm.acompletion(
                model=body.model,
                messages=[m.model_dump() for m in body.messages],
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
            model=body.model,
            messages=[m.model_dump() for m in body.messages],
        )
        content = completion["choices"][0]["message"]["content"]
        return ChatResponse(message=ChatMessage(role="assistant", content=content))

    @router.get("/api/show", response_model=ModelInfo)
    async def show(name: str) -> ModelInfo:
        tag_list = (await tags()).models
        for m in tag_list:
            if m.model == name:
                return m
        raise HTTPException(status_code=404, detail="model not found")

    app.include_router(router)
    return app


def main() -> None:  # pragma: no cover - entry point
    import uvicorn

    uvicorn.run(
        build_app(),
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "4000")),
    )

