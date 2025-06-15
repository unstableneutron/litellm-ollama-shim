"""Pydantic models representing Ollama-style API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class TagDetails(BaseModel):
    """Metadata for a model tag."""

    family: str
    format: str
    parameter_size: str


class Tag(BaseModel):
    """Information about an available model."""

    name: str
    model: str
    modified_at: datetime
    size: int
    digest: str
    details: TagDetails


class TagsResponse(BaseModel):
    """Response payload for the `/api/tags` endpoint."""

    models: list[Tag]


class ChatMessage(BaseModel):
    """One message in a conversation."""

    role: str
    content: str


class ChatRequest(BaseModel):
    """Request payload for the `/api/chat` endpoint."""

    model: str
    messages: list[ChatMessage]
    stream: bool = False


class ChatResponseMessage(BaseModel):
    """Chat completion message returned by the model."""

    role: str
    content: str


class ChatResponse(BaseModel):
    """Response payload for non-streaming chat completions."""

    message: ChatResponseMessage


ShowResponse = Tag
