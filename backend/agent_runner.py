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


# Prompt yêu cầu "Final Answer:" nhưng LLM hay viết tắt thành "Final:".
# Bắt cả 2 dạng, nếu không agent sẽ chạy phí vòng lặp rồi rơi vào guardrail
# dù đã có sẵn câu trả lời.
FINAL_RE = re.compile(r'Final\s*(?:Answer)?\s*:', re.IGNORECASE)


def _split_final(text: str):
    """Trả về phần Final Answer nếu có, ngược lại None."""
    m = FINAL_RE.search(text)
    return text[m.end():].strip() if m else None


def _action_signature(tool_name: str, kwargs: dict) -> tuple:
    return (tool_name, json.dumps(kwargs, sort_keys=True, ensure_ascii=False))


def _call_tool(tool_name: str, kwargs: dict, executed_actions: set) -> str:
    """Gọi tool từ AVAILABLE_TOOLS, trả về chuỗi Observation. Không bao giờ raise."""
    signature = _action_signature(tool_name, kwargs)

    if tool_name not in AVAILABLE_TOOLS:
        valid = ", ".join(AVAILABLE_TOOLS.keys())
        return f"LỖI: Tool '{tool_name}' không tồn tại. Tool hợp lệ: [{valid}]."

    if signature in executed_actions:
        return (
            f"LỖI: Action {tool_name}({kwargs}) đã được gọi trước đó, không lặp lại. "
            "Hãy dùng kết quả đã có để đưa ra Final Answer."
        )

    fn = AVAILABLE_TOOLS[tool_name]
    try:
        observation = fn(*kwargs["__pos__"]) if "__pos__" in kwargs else fn(**kwargs)
    except TypeError as e:
        return f"LỖI: Tham số không hợp lệ khi gọi '{tool_name}' — {e}"
    except Exception as e:
        return f"LỖI: Ngoại lệ khi thực thi '{tool_name}' — {e}"

    executed_actions.add(signature)
    return observation


def generate_nonempty(provider, prompt: str, system_prompt: str = "", retries: int = 1) -> str:
    """
    Gọi LLM và đảm bảo không nhận về chuỗi rỗng.

    Một số provider (DeepSeek, Gemini...) thỉnh thoảng trả content=None hoặc chuỗi
    trắng. Nếu để nguyên, UI sẽ hiện bong bóng trống. Thử lại tối đa `retries` lần.
    """
    for _ in range(retries + 1):
        try:
            out = provider.generate(prompt, system_prompt=system_prompt)
        except Exception:
            return ""
        if out and out.strip():
            return out
    return ""


def _looks_like_answer(text: str) -> bool:
    """
    Đúng khi LLM viết thẳng câu trả lời cho người dùng mà quên nhãn 'Final Answer:'.
    Dùng để không lãng phí lượt lặp và không rơi guardrail oan.
    """
    stripped = re.sub(r'^\s*Thought:\s*', '', text.strip(), flags=re.IGNORECASE)
    if len(stripped) < 80:
        return False
    return "Action:" not in stripped


# Quy tắc chung cho MỌI câu trả lời gửi tới người dùng, ở mọi cấp độ.
# Đặt SAU prompt gốc để ghi đè chỉ dẫn "Nêu rõ kết quả nào đến từ tool" trong
# REACT_SYSTEM_PROMPT (src/prompts.py của Role 3) — người dùng cuối không cần
# và không nên thấy tên hàm hay cơ chế nội bộ.
NO_SYSTEM_LEAK = """

QUY TẮC BẮT BUỘC VỀ NỘI DUNG TRẢ LỜI CHO NGƯỜI DÙNG:
- TUYỆT ĐỐI không nhắc tên tool/hàm nội bộ (analyze_mbti_match,
  calculate_zodiac_compatibility, suggest_date_ideas...) trong câu trả lời.
- Không dùng các cụm lộ cơ chế: "theo tool", "tool trả về", "dựa trên tool",
  "Observation", "system prompt", "agent", "cấp độ", "baseline", "hệ thống của
  tôi", "bộ nhớ của tôi", "tập luật", "keyword".
- Nói như một người tư vấn thật: đưa thẳng kết quả và nhận định, không mô tả
  mình lấy nó từ đâu trong hệ thống.
  SAI: "Theo tool analyze_mbti_match, INTJ và ENFP đạt 95%."
  ĐÚNG: "INTJ và ENFP có độ tương thích 95%."
- Vẫn giữ nguyên tắc trung thực: không bịa số liệu, tên người hay điểm tương
  thích; nếu không có dữ liệu thì nói chưa có thông tin, diễn đạt tự nhiên."""


# Giữ tên cũ để phần baseline dùng lại, gộp thêm quy tắc giọng điệu riêng.
_NO_META_SUFFIX = NO_SYSTEM_LEAK + """
- Khi người dùng chỉ chào hỏi hoặc hỏi kiến thức chung, cứ trả lời tự nhiên,
  không rào đón về khả năng của bản thân."""


def run_baseline(user_query: str, provider, context: str = "") -> str:
    """Chatbot Baseline: 1 lượt gọi LLM, không tool. Trả thẳng chuỗi response."""
    system = CHATBOT_BASELINE_PROMPT + _NO_META_SUFFIX
    if context:
        system += f"\n\n{context}"
    return provider.generate(user_query, system_prompt=system)


def stream_react_agent(user_query: str, provider, context: str = ""):
    """
    Generator yield từng step của ReAct loop dạng dict, để backend/main.py
    chuyển thành SSE. Mỗi dict có key "type":
      - "thought"     {"type", "step", "content"}
      - "action"      {"type", "step", "tool", "args"}
      - "observation" {"type", "step", "content"}  (kết quả tool thật)
      - "notice"      {"type", "step", "content"}  (nhắc nhở của hệ thống)
      - "final"       {"type", "step", "content"}
      - "guardrail"   {"type", "step", "content"}
      - "error"       {"type", "step", "content"}
    """
    conversation = f"Question: {user_query}\n"
    executed_actions = set()
    observations: list[str] = []
    step = 0
    system = REACT_SYSTEM_PROMPT + NO_SYSTEM_LEAK + (f"\n\n{context}" if context else "")

    while step < MAX_ITERATIONS:
        step += 1

        try:
            llm_output = provider.generate(conversation, system_prompt=system)
        except Exception as e:
            yield {"type": "error", "step": step, "content": f"Lỗi khi gọi LLM Provider: {e}"}
            return

        tool_name, kwargs = _parse_action(llm_output)

        # Chỉ coi là kết thúc khi KHÔNG còn Action nào cần chạy, tránh cắt sớm
        # trường hợp model viết cả Action lẫn Final trong một lượt.
        final = _split_final(llm_output)
        if final and not tool_name:
            yield {"type": "final", "step": step, "content": final}
            return

        thought = _extract_thought(llm_output)
        if thought:
            yield {"type": "thought", "step": step, "content": thought}

        if tool_name:
            # Kiểm tra trùng lặp TRƯỚC khi báo Action, để trace không hiển thị
            # một lần gọi tool thành công trong khi thực tế đã bị chặn.
            if _action_signature(tool_name, kwargs or {}) in executed_actions:
                warn = (
                    f"Đã chặn gọi lại {tool_name} với cùng tham số. "
                    "Hãy dùng kết quả đã có để kết luận."
                )
                yield {"type": "guardrail", "step": step, "content": warn}
                conversation += llm_output.strip() + f"\nObservation: {warn}\n"
                continue

            yield {"type": "action", "step": step, "tool": tool_name, "args": kwargs}
            obs = _call_tool(tool_name, kwargs or {}, executed_actions)
            observations.append(obs)
            yield {"type": "observation", "step": step, "content": obs}
            conversation += llm_output.strip() + "\n"
            conversation += f"Observation: {obs}\n"
            continue

        # Không có Action: nếu LLM đã viết thẳng câu trả lời (chỉ quên nhãn
        # "Final Answer:") thì nhận luôn, tránh lãng phí lượt lặp và tránh
        # rơi guardrail oan dù đã có sẵn đáp án.
        if _looks_like_answer(llm_output):
            answer = re.sub(r'^\s*Thought:\s*', '', llm_output.strip(), flags=re.IGNORECASE)
            yield {"type": "final", "step": step, "content": answer}
            return

        obs = "Không tìm thấy Action hợp lệ. Hãy đưa ra Final Answer hoặc thử Action khác."
        yield {"type": "notice", "step": step, "content": obs}
        conversation += llm_output.strip() + "\n"
        conversation += f"Observation: {obs}\n"

    # Hết budget. Nếu đã thu được dữ liệu từ tool thì vẫn trả về cho người dùng
    # thay vì vứt đi và xin lỗi suông.
    if observations:
        usable = [o for o in observations if not o.startswith("LỖI:")]
        if usable:
            yield {
                "type": "guardrail",
                "step": step,
                "content": (
                    f"Đã đạt giới hạn {MAX_ITERATIONS} bước nên mình dừng suy luận tại đây. "
                    "Dưới đây là dữ liệu mình đã tra cứu được:\n\n"
                    + "\n".join(f"• {o}" for o in usable)
                    + "\n\nBạn có thể hỏi cụ thể hơn để mình phân tích sâu hơn nhé."
                ),
            }
            return

    yield {
        "type": "guardrail",
        "step": step,
        "content": (
            f"Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước. Xin lỗi, mình chưa thu thập đủ dữ liệu "
            "đáng tin cậy để kết luận trong giới hạn số bước cho phép. Bạn vui lòng cung cấp thêm "
            "thông tin cụ thể để mình hỗ trợ tiếp nhé."
        ),
    }
