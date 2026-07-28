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
from levels import run_rule_based, stream_autonomous_agent
from schemas import BaselineResponse, ChatRequest, HealthResponse

app = FastAPI(title="Cupid Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):5173|https://.*\.ngrok(-free)?\.(app|io)",
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


def _sse(generator):
    """Bọc generator step-dict thành SSE response."""

    def event_stream():
        for event in generator:
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/api/chat/level1", response_model=BaselineResponse)
def chat_level1(req: ChatRequest):
    """Cấp độ 1 — Rule-Based Bot: khớp từ khóa if/else, không LLM, không tool."""
    return BaselineResponse(response=run_rule_based(req.query))


@app.post("/api/chat/baseline", response_model=BaselineResponse)
def chat_baseline(req: ChatRequest):
    """Cấp độ 2 — LLM Chatbot: sinh text mượt nhưng không gọi được tool."""
    provider = get_llm_provider()
    response = run_baseline(req.query, provider)
    return BaselineResponse(response=response)


@app.post("/api/chat/react")
def chat_react(req: ChatRequest):
    """Cấp độ 3 — ReAct Agent: Thought -> Action -> Observation, có gọi tool."""
    provider = get_llm_provider()
    return _sse(stream_react_agent(req.query, provider))


@app.post("/api/chat/autonomous")
def chat_autonomous(req: ChatRequest):
    """Cấp độ 4 — Autonomous Agent: tự lập kế hoạch, có Memory, tự đánh giá."""
    provider = get_llm_provider()
    return _sse(stream_autonomous_agent(req.query, provider))
