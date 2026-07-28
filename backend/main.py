"""
FastAPI backend cho Cupid Agent Web UI.
Bọc lại tools.py + prompts.py + providers.py (src/) qua REST + SSE,
phục vụ frontend React trace trực quan luồng ReAct (Thought -> Action -> Observation).
"""

import json
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from providers import get_llm_provider

from agent_runner import run_baseline, stream_react_agent
from schemas import BaselineResponse, ChatRequest, HealthResponse

app = FastAPI(title="Cupid Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@app.get("/api/health", response_model=HealthResponse)
def health():
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    return HealthResponse(provider=provider.__class__.__name__, model=model_name)


@app.get("/api/test-cases")
def test_cases():
    path = os.path.join(REPO_ROOT, "config", "test_cases.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.post("/api/chat/baseline", response_model=BaselineResponse)
def chat_baseline(req: ChatRequest):
    provider = get_llm_provider()
    response = run_baseline(req.query, provider)
    return BaselineResponse(response=response)


@app.post("/api/chat/react")
def chat_react(req: ChatRequest):
    provider = get_llm_provider()

    def event_stream():
        for event in stream_react_agent(req.query, provider):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
