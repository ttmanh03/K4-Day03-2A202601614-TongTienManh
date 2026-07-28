"""Pydantic request/response models cho FastAPI backend."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str


class BaselineResponse(BaseModel):
    response: str


class HealthResponse(BaseModel):
    provider: str
    model: str
