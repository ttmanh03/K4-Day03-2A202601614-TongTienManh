"""Pydantic request/response models cho FastAPI backend."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    session_id: str = "default"


class BaselineResponse(BaseModel):
    response: str
    # Chỉ Cấp 1 dùng: id của luật if/else đã khớp (hoặc "fallback")
    matched_rule: str | None = None


class HealthResponse(BaseModel):
    provider: str
    model: str
