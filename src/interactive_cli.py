"""
💬 CUPID AGENT — INTERACTIVE TERMINAL CLI (CHẾ ĐỘ TƯƠNG TÁC GÕ NHẬP TỰ DO)
Cho phép người dùng gõ nhập bất kỳ câu hỏi tùy ý trực tiếp trên Terminal console!
"""

import sys
import os

# Ensure src/ is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import run_react_agent, run_baseline_chatbot
from providers import get_llm_provider


def main():
    print("==================================================")
    print("💘 CUPID AGENT — CHẾ ĐỘ TƯƠNG TÁC NHẬP DỮ LIỆU TỰ DO")
    print("==================================================")
    
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Mock Engine")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} ({model_name})")
    print("💡 Gõ 'exit' hoặc 'quit' để thoát chương trình.\n")

    while True:
        try:
            user_input = input("💬 Nhập câu hỏi tư vấn tình cảm / ghép đôi của bạn: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q", "thoát"]:
                print("👋 Cảm ơn bạn đã sử dụng Cupid Agent. Tạm biệt!")
                break

            print("\n--------------------------------------------------")
            print("1. CHATBOT BASELINE (Không Tool)")
            print("--------------------------------------------------")
            run_baseline_chatbot(user_input, provider)

            print("\n--------------------------------------------------")
            print("2. REACT AGENT LOOP (Có Tool & Trace)")
            print("--------------------------------------------------")
            run_react_agent(user_input, provider)
            print("\n==================================================\n")

        except (KeyboardInterrupt, EOFError):
            print("\n👋 Đã thoát chế độ tương tác.")
            break


if __name__ == "__main__":
    main()
