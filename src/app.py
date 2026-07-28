"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import json
import os
import sys
from dotenv import load_dotenv

# Đảm bảo import các module cùng thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import các thành phần từ file của Role 2, Role 3 & Multi-Provider Adapter
import re
from tools import AVAILABLE_TOOLS
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()

def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    
    # Fallback kiểm tra nếu file ở thư mục hiện tại
    if not os.path.exists(config_path):
        config_path = "test_cases.json"
        
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_baseline_chatbot(user_query: str, provider):
    """
    Dựng Chatbot gốc (Baseline) không có công cụ.
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    print(f"⚙️ System Prompt: {CHATBOT_BASELINE_PROMPT.strip()}")
    
    # Gọi LLM Provider thực hiện sinh câu trả lời
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")


def _parse_action(text: str):
    """Trích xuất (tool_name, kwargs_dict) từ dòng 'Action: name({...})'. Trả (None,None) nếu không có."""
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
    # Positional fallback: "val1", "val2"
    parts = [p.strip().strip('"\'' ) for p in raw.split(',') if p.strip()]
    return tool_name, {"__pos__": parts} if parts else {}


def _call_tool(tool_name: str, kwargs: dict) -> str:
    """Gọi tool từ AVAILABLE_TOOLS, trả về chuỗi Observation."""
    if tool_name not in AVAILABLE_TOOLS:
        valid = ", ".join(AVAILABLE_TOOLS.keys())
        return f"LỖI: Tool '{tool_name}' không tồn tại. Tool hợp lệ: [{valid}]."
    fn = AVAILABLE_TOOLS[tool_name]
    try:
        if "__pos__" in kwargs:
            return fn(*kwargs["__pos__"])
        return fn(**kwargs)
    except TypeError as e:
        return f"LỖI: Tham số không hợp lệ khi gọi '{tool_name}' — {e}"
    except Exception as e:
        return f"LỖI: Ngoại lệ khi thực thi '{tool_name}' — {e}"


def run_react_agent(user_query: str, provider):
    """
    Vòng lặp ReAct Agent (Thought -> Action -> Observation) có Guardrails.
    Gọi LLM thực sự, parse Action, thực thi tool, cập nhật context.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    conversation = f"Question: {user_query}\n"
    step = 0

    while step < MAX_ITERATIONS:
        step += 1
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")

        llm_output = provider.generate(conversation, system_prompt=REACT_SYSTEM_PROMPT)
        print(f"📝 LLM Output:\n{llm_output}")

        # Trường hợp 1: Final Answer
        if "Final Answer:" in llm_output:
            idx = llm_output.index("Final Answer:")
            final = llm_output[idx + len("Final Answer:"):].strip()
            print(f"\n🏁 Final Answer:\n{final}")
            return

        # Trường hợp 2: Action
        tool_name, kwargs = _parse_action(llm_output)
        if tool_name:
            print(f"🛠️ Action: {tool_name}({kwargs})")
            obs = _call_tool(tool_name, kwargs or {})
            print(f"👁️ Observation: {obs}")
            conversation += llm_output.strip() + "\n"
            conversation += f"Observation: {obs}\n"
        else:
            print("⚠️ Không parse được Action — thêm gợi ý vào context.")
            conversation += llm_output.strip() + "\n"
            conversation += "Observation: Không tìm thấy Action hợp lệ. Hãy đưa ra Final Answer hoặc thử Action khác.\n"

    print(f"\n🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước. Ngắt lặp an toàn!")


if __name__ == "__main__":
    print("==================================================")
    print("💘 CUPID AGENT — CHATBOT vs REACT AGENT")
    print("   VinUni AI Codelab × GDGoC — Lab 03")
    print("==================================================")

    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})")

    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json\n")

    for tc in tests:
        print(f"\n{'#'*55}")
        print(f"  TEST CASE {tc['id']}: {tc['category']}")
        print(f"{'#'*55}")
        print(f"  📋 Câu hỏi: {tc['question']}")
        print(f"  🎯 Kỳ vọng: {tc['expected_behavior']}")

        print(f"\n--- DEMO 1: CHATBOT BASELINE ---")
        run_baseline_chatbot(tc["question"], provider)

        print(f"\n--- DEMO 2: REACT AGENT ---")
        run_react_agent(tc["question"], provider)

    print(f"\n{'='*55}")
    print("🏆 Hoàn tất chạy 5 Test Cases! Phân tích trace bên trên.")
    print(f"{'='*55}")

