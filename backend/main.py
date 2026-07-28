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

import memory
from agent_runner import run_baseline, stream_react_agent
from levels import match_rule, stream_autonomous_agent
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
    """Bọc generator step-dict thành SSE (không đụng tới memory)."""

    def event_stream():
        for event in generator:
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def _sse_with_memory(generator, session_id: str, query: str, provider):
    """
    Bọc generator step-dict thành SSE. Sau khi stream xong, lưu lượt hội thoại
    vào short-term memory và nhờ LLM trích fact vào long-term memory; nếu có
    fact mới thì bắn thêm 1 event "memory_saved" để UI hiển thị.
    """

    def event_stream():
        final_text = ""
        for event in generator:
            if event["type"] in ("final", "guardrail"):
                final_text = event.get("content", "")
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

        if final_text:
            memory.add_turn(session_id, query, final_text)
            new_facts = memory.extract_and_store(session_id, query, final_text, provider)
            if new_facts:
                event = {
                    "type": "memory_saved",
                    "step": 0,
                    "content": "Đã ghi nhớ dài hạn: "
                    + "; ".join(f"{k} = {v}" for k, v in new_facts.items()),
                }
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/api/memory/{session_id}")
def read_memory(session_id: str):
    """Xem bộ nhớ hiện tại của một session (phục vụ demo & chấm điểm)."""
    return {
        "long_term": memory.get_long_term(session_id),
        "short_term": memory.get_recent_turns(session_id),
    }


@app.delete("/api/memory/{session_id}")
def reset_memory(session_id: str):
    memory.clear_memory(session_id)
    return {"status": "cleared"}


@app.get("/api/rules")
def rules():
    """Trả knowledge base của Cấp 1 (luật if/else + test case) để demo/chấm điểm."""
    path = os.path.join(REPO_ROOT, "config", "rule_based_kb.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.post("/api/chat/level1", response_model=BaselineResponse)
def chat_level1(req: ChatRequest):
    """Cấp độ 1 — Rule-Based Bot: khớp từ khóa if/else, không LLM, không tool.

    Cấp 1 KHÔNG dùng memory: bot luật cố định không có khái niệm ngữ cảnh.
    """
    rule_id, response = match_rule(req.query)
    return BaselineResponse(response=response, matched_rule=rule_id)


@app.post("/api/chat/baseline", response_model=BaselineResponse)
def chat_baseline(req: ChatRequest):
    """Cấp độ 2 — LLM Chatbot: sinh text mượt nhưng không gọi được tool.

    KHÔNG dùng memory: theo bảng 4 cấp độ, Memory là đặc trưng của Cấp 4.
    Chatbot ở đây trả lời độc lập từng lượt, không nhớ hội thoại trước.
    """
    provider = get_llm_provider()
    return BaselineResponse(response=run_baseline(req.query, provider))


@app.post("/api/chat/react")
def chat_react(req: ChatRequest):
    """Cấp độ 3 — ReAct Agent: Thought -> Action -> Observation, có gọi tool.

    KHÔNG dùng memory: nếu cho agent nhớ câu trả lời cũ, nó sẽ trả lời thẳng từ
    lịch sử thay vì gọi tool, làm mất đúng đặc trưng cần demo của Cấp 3.
    """
    provider = get_llm_provider()
    return _sse(stream_react_agent(req.query, provider))


@app.post("/api/chat/autonomous")
def chat_autonomous(req: ChatRequest):
    """Cấp độ 4 — Autonomous Agent: tự lập kế hoạch, có Memory, tự đánh giá.

    Cấp DUY NHẤT có Memory: short-term 5 lượt gần nhất + long-term do LLM trích xuất.
    """
    provider = get_llm_provider()
    context = memory.build_context(req.session_id)
    gen = stream_autonomous_agent(req.query, provider, context)
    return _sse_with_memory(gen, req.session_id, req.query, provider)
