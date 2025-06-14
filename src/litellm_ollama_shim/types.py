from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel


class TagDetails(BaseModel):
    family: str
    format: str
    parameter_size: str


class Tag(BaseModel):
    name: str
    model: str
    modified_at: datetime
    size: int
    digest: str
    details: TagDetails


class TagsResponse(BaseModel):
    models: List[Tag]


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: bool = False


class ChatResponseMessage(BaseModel):
    role: str
    content: str


class ChatResponse(BaseModel):
    message: ChatResponseMessage


ShowResponse = Tag
