"""
🌟 DEMO TỔNG HỢP 4 CẤP ĐỘ AI (LEVEL 1 -> LEVEL 4)
Chạy lần lượt từ Rule-Based Bot (Cấp 1) đến Autonomous Agent (Cấp 4).
"""

import os
import sys

# Ensure src/ is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from level1_rule_based import rule_based_bot
from level2_llm_chatbot import llm_chatbot
from level3_reactive_agent import reactive_agent_demo
from level4_autonomous_agent import AutonomousAgent
from providers import get_llm_provider


def run_all_4_levels():
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Mock")
    
    print("=================================================================")
    print("🚀 DEMO SO SÁNH 4 CẤP ĐỘ AI AGENT (VINUNI LAB 03 × GDGOC)")
    print(f"🔌 LLM Provider: {provider.__class__.__name__} (Model: {model_name})")
    print("=================================================================\n")

    query = "Tôi là INTJ và người ấy là ENFP. Chúng tôi có hợp nhau không? Nếu có, hãy gợi ý một buổi hẹn hò lãng mạn ở Hà Nội với ngân sách trung bình."
    print(f"📋 CÂU HỎI KIỂM THỬ: \"{query}\"\n")

    # CẤP 1
    print("-----------------------------------------------------------------")
    print("🤖 [CẤP 1: RULE-BASED BOT] — Match từ khóa cố định, 0 LLM API")
    print("-----------------------------------------------------------------")
    print(f"Phản hồi: {rule_based_bot(query)}\n")

    # CẤP 2
    print("-----------------------------------------------------------------")
    print("💬 [CẤP 2: LLM CHATBOT] — LLM sinh text mượt, Không dùng được Tool")
    print("-----------------------------------------------------------------")
    print(f"Phản hồi:\n{llm_chatbot(query, provider)}\n")

    # CẤP 3
    print("-----------------------------------------------------------------")
    print("🤖 [CẤP 3: REACTIVE AGENT] — ReAct Loop (Thought -> Action -> Observation)")
    print("-----------------------------------------------------------------")
    reactive_agent_demo(query, provider)
    print("\n")

    # CẤP 4
    print("-----------------------------------------------------------------")
    print("🚀 [CẤP 4: AUTONOMOUS AGENT] — Planning + Memory + Self-Reflection")
    print("-----------------------------------------------------------------")
    auto_agent = AutonomousAgent(provider)
    auto_agent.run_autonomous_flow(query)

    print("\n=================================================================")
    print("🏆 HOÀN THÀNH DEMO SO SÁNH 4 CẤP ĐỘ AI AGENT!")
    print("=================================================================")


if __name__ == "__main__":
    run_all_4_levels()
