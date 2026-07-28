"""
🤖 CẤP ĐỘ 3: REACTIVE AGENT (ReAct Loop: Thought -> Action -> Observation)
Sử dụng LLM API Key + Đăng ký công cụ (Tools) + Phanh an toàn Guardrails.
"""

import os
import sys

# Ensure src/ is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import run_react_agent
from providers import get_llm_provider


def reactive_agent_demo(user_input: str, provider=None):
    if provider is None:
        provider = get_llm_provider()
    
    run_react_agent(user_input, provider)


if __name__ == "__main__":
    print("==================================================")
    print("🤖 DEMO CẤP ĐỘ 3: REACTIVE AGENT (REACT LOOP + TOOLS)")
    print("==================================================")
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Mock")
    print(f"🔌 Using LLM Provider: {provider.__class__.__name__} ({model_name})\n")

    query = "Tôi là INTJ và người ấy là ENFP. Chúng tôi có hợp nhau không? Nếu có, hãy gợi ý một buổi hẹn hò lãng mạn ở Hà Nội với ngân sách trung bình."
    reactive_agent_demo(query, provider)
