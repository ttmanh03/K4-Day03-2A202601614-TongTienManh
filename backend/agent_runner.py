"""
Bản streaming của ReAct Agent loop, dùng cho backend FastAPI.

Logic parse Action / gọi tool / vòng lặp Thought-Action-Observation được
chuyển thể tay từ `src/app.py` (hàm `_parse_action`, `_call_tool`,
`run_react_agent`), đổi từ print() sang generator yield step-dict để
stream qua SSE. KHÔNG sửa `src/app.py` — nếu app.py đổi cách parse Action,
cần đồng bộ tay lại các hàm dưới đây.
"""

import json
import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from tools import AVAILABLE_TOOLS
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS


def _parse_action(text: str):
    """Trích xuất (tool_name, kwargs_dict) từ dòng 'Action: name({...})'. Trả (None, None) nếu không có."""
    m = re.search(r'Action:\s*(\w+)\s*\((.*)\)\s*$', text, re.MULTILINE | re.DOTALL)
    if not m:
        return None, None
    tool_name = m.group(1).strip()
    raw = m.group(2).strip()
    try:
        kwargs = json.loads(raw)
        if isinstance(kwargs, dict):
            return tool_name, kwargs
    except (json.JSONDecodeError, ValueError):
        pass
    parts = [p.strip().strip('"\'') for p in raw.split(',') if p.strip()]
    return tool_name, {"__pos__": parts} if parts else {}


def _extract_thought(text: str) -> str:
    """Lấy phần 'Thought: ...' đứng trước dòng Action (nếu có), để hiển thị tách riêng khỏi Action."""
    m = re.search(r'Thought:\s*(.*?)(?=\n\s*Action:|\Z)', text, re.DOTALL)
    return m.group(1).strip() if m else text.strip()


def _call_tool(tool_name: str, kwargs: dict, executed_actions: set) -> str:
    """Gọi tool từ AVAILABLE_TOOLS, trả về chuỗi Observation. Không bao giờ raise."""
    signature = (tool_name, json.dumps(kwargs, sort_keys=True, ensure_ascii=False))

    if tool_name not in AVAILABLE_TOOLS:
        valid = ", ".join(AVAILABLE_TOOLS.keys())
        return f"LỖI: Tool '{tool_name}' không tồn tại. Tool hợp lệ: [{valid}]."

    if signature in executed_actions:
        return f"LỖI: Action {tool_name}({kwargs}) đã được gọi trước đó, không lặp lại. Hãy thử cách khác hoặc kết luận."

    fn = AVAILABLE_TOOLS[tool_name]
    try:
        observation = fn(*kwargs["__pos__"]) if "__pos__" in kwargs else fn(**kwargs)
    except TypeError as e:
        return f"LỖI: Tham số không hợp lệ khi gọi '{tool_name}' — {e}"
    except Exception as e:
        return f"LỖI: Ngoại lệ khi thực thi '{tool_name}' — {e}"

    executed_actions.add(signature)
    return observation


def run_baseline(user_query: str, provider) -> str:
    """Chatbot Baseline: 1 lượt gọi LLM, không tool. Trả thẳng chuỗi response."""
    return provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)


def stream_react_agent(user_query: str, provider):
    """
    Generator yield từng step của ReAct loop dạng dict, để backend/main.py
    chuyển thành SSE. Mỗi dict có key "type":
      - "thought"     {"type", "step", "content"}
      - "action"      {"type", "step", "tool", "args"}
      - "observation" {"type", "step", "content"}
      - "final"       {"type", "step", "content"}
      - "guardrail"   {"type", "step", "content"}
      - "error"       {"type", "step", "content"}
    """
    conversation = f"Question: {user_query}\n"
    executed_actions = set()
    step = 0

    while step < MAX_ITERATIONS:
        step += 1

        try:
            llm_output = provider.generate(conversation, system_prompt=REACT_SYSTEM_PROMPT)
        except Exception as e:
            yield {"type": "error", "step": step, "content": f"Lỗi khi gọi LLM Provider: {e}"}
            return

        if "Final Answer:" in llm_output:
            idx = llm_output.index("Final Answer:")
            final = llm_output[idx + len("Final Answer:"):].strip()
            yield {"type": "final", "step": step, "content": final}
            return

        yield {"type": "thought", "step": step, "content": _extract_thought(llm_output)}

        tool_name, kwargs = _parse_action(llm_output)
        if tool_name:
            yield {"type": "action", "step": step, "tool": tool_name, "args": kwargs}
            obs = _call_tool(tool_name, kwargs or {}, executed_actions)
            yield {"type": "observation", "step": step, "content": obs}
            conversation += llm_output.strip() + "\n"
            conversation += f"Observation: {obs}\n"
        else:
            obs = "Không tìm thấy Action hợp lệ. Hãy đưa ra Final Answer hoặc thử Action khác."
            yield {"type": "observation", "step": step, "content": obs}
            conversation += llm_output.strip() + "\n"
            conversation += f"Observation: {obs}\n"

    yield {
        "type": "guardrail",
        "step": step,
        "content": (
            f"Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước. Xin lỗi, mình chưa thu thập đủ dữ liệu "
            "đáng tin cậy để kết luận trong giới hạn số bước cho phép. Bạn vui lòng cung cấp thêm "
            "thông tin cụ thể để mình hỗ trợ tiếp nhé."
        ),
    }
