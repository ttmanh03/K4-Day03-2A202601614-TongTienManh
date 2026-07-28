"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import json
import os
import re
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
from tools import AVAILABLE_TOOLS
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()

# Action theo hợp đồng của Role 3: Action: tool_name({"param": "value"})
ACTION_PATTERN = re.compile(r"Action:\s*(\w+)\((\{.*?\})\)", re.DOTALL)
FINAL_ANSWER_PATTERN = re.compile(r"Final Answer:\s*(.+)", re.DOTALL)

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


def _execute_action(tool_name: str, raw_args: str, executed_actions: set) -> str:
    """Thực thi 1 Action mà LLM yêu cầu. Luôn trả về chuỗi Observation, không bao giờ crash."""
    signature = (tool_name, raw_args)

    if tool_name not in AVAILABLE_TOOLS:
        return f"LỖI: Tool '{tool_name}' không tồn tại trong danh sách tool hợp lệ."

    if signature in executed_actions:
        return f"LỖI: Action {tool_name}({raw_args}) đã được gọi trước đó, không lặp lại. Hãy thử cách khác hoặc kết luận."

    try:
        kwargs = json.loads(raw_args)
    except json.JSONDecodeError as e:
        return f"LỖI: Tham số JSON không hợp lệ cho tool '{tool_name}': {e}"

    try:
        observation = AVAILABLE_TOOLS[tool_name](**kwargs)
    except TypeError as e:
        return f"LỖI: Tham số không khớp với tool '{tool_name}': {e}"

    executed_actions.add(signature)
    return observation


def run_react_agent(user_query: str, provider):
    """
    Vòng lặp ReAct Agent thật (Thought -> Action -> Observation) có Guardrails.
    Parse Action dạng JSON theo đúng hợp đồng mà Role 3 định nghĩa trong prompts.py.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")

    history = f"Câu hỏi của người dùng: {user_query}"
    executed_actions = set()

    for step in range(1, MAX_ITERATIONS + 1):
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")

        response = provider.generate(history, system_prompt=REACT_SYSTEM_PROMPT)
        print(response.strip())

        final_match = FINAL_ANSWER_PATTERN.search(response)
        action_match = ACTION_PATTERN.search(response)

        # Final Answer chỉ được chấp nhận nếu không có Action nào đứng trước nó
        if final_match and not (action_match and action_match.start() < final_match.start()):
            return

        if not action_match:
            observation = "LỖI: Phản hồi không đúng định dạng Action/Final Answer yêu cầu."
        else:
            tool_name, raw_args = action_match.groups()
            observation = _execute_action(tool_name, raw_args, executed_actions)

        print(f"👁️ Observation: {observation}")
        history += f"\n{response.strip()}\nObservation: {observation}"

    print(f"🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước. Ngắt lặp an toàn!")
    print("🏁 Final Answer (fallback an toàn): Xin lỗi, mình chưa thu thập đủ dữ liệu đáng tin cậy để kết luận trong giới hạn số bước cho phép. Bạn vui lòng cung cấp thêm thông tin cụ thể để mình hỗ trợ tiếp nhé.")


if __name__ == "__main__":
    print("==================================================")
    print("🏫 ĐẠI HỌC VINUNI - BÀI LAB 3: CHATBOT VS REACT AGENT")
    print("==================================================")
    
    # Khởi tạo Multi-Provider LLM Adapter (Đọc từ biến môi trường LLM_PROVIDER)
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})")
    
    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json\n")
    
    # Chạy thử câu test số 3
    sample_query = tests[2]["question"]
    
    print("--- DEMO 1: CHẠY TRÊN CHATBOT BASELINE ---")
    run_baseline_chatbot(sample_query, provider)
    
    print("\n--- DEMO 2: CHẠY TRÊN REACT AGENT ---")
    run_react_agent(sample_query, provider)
