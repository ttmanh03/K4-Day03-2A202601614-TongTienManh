"""
💬 CẤP ĐỘ 2: LLM CHATBOT (Dùng LLM API sinh văn bản mượt, không có Tool)
Sử dụng API Key thực tế (Gemini, OpenAI, Anthropic, OpenRouter hoặc Mock).
"""

import os
import sys

# Ensure src/ is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompts import CHATBOT_BASELINE_PROMPT
from providers import get_llm_provider


def llm_chatbot(user_input: str, provider=None) -> str:
    if provider is None:
        provider = get_llm_provider()
    
    # LLM nhận System Prompt cấm gọi tool
    response = provider.generate(user_input, system_prompt=CHATBOT_BASELINE_PROMPT)
    return response


if __name__ == "__main__":
    print("==================================================")
    print("💬 DEMO CẤP ĐỘ 2: LLM CHATBOT (TEXT GENERATION ONLY)")
    print("==================================================")
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Mock")
    print(f"🔌 Using LLM Provider: {provider.__class__.__name__} ({model_name})\n")

    test_queries = [
        "Tôi là INTJ và người ấy là ENFP, chúng tôi có hợp nhau không?",
        "Gợi ý cho tôi một buổi hẹn hò ở Hà Nội."
    ]
    for q in test_queries:
        print(f"💬 Query: {q}")
        print(f"🤖 Chatbot (Cấp 2):\n{llm_chatbot(q, provider)}\n")
