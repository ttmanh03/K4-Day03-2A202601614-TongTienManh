"""
💬 CUPID AGENT — TERMINAL INTERACTIVE CHAT ENGINE (USING REAL LLM API)
Trò chuyện tương tác trực tiếp với ReAct Agent trong Terminal qua Gemini / OpenAI / Mock API!
"""

import sys
import os

# Ensure src/ is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import run_react_agent
from providers import get_llm_provider, GeminiProvider, OpenAIProvider, MockProvider
from dotenv import load_dotenv

load_dotenv()


def print_banner(provider):
    provider_name = provider.__class__.__name__
    model_name = getattr(provider, "model_name", "Offline Engine")
    
    print("=================================================================")
    print("💘 CUPID AGENT — TERMINAL INTERACTIVE CHAT (API MODE)")
    print(f"🔌 active LLM Provider: {provider_name} (Model: {model_name})")
    print("-----------------------------------------------------------------")
    print("💡 LỆNH ĐẶC BIỆT:")
    print("   • Type '/switch gemini'   : Chuyển sang dùng Google Gemini API Key")
    print("   • Type '/switch openai'   : Chuyển sang dùng OpenAI GPT API Key")
    print("   • Type '/switch mock'     : Chuyển sang dùng Mock Engine (Offline)")
    print("   • Type 'exit' hoặc 'quit' : Thoát chương trình")
    print("=================================================================\n")


def main():
    provider = get_llm_provider()
    print_banner(provider)

    while True:
        try:
            user_input = input("💬 User > ").strip()
            
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q", "thoát"]:
                print("👋 Cảm ơn bạn đã trò chuyện cùng Cupid Agent. Tạm biệt!")
                break

            # Command switching provider on the fly
            if user_input.lower().startswith("/switch"):
                parts = user_input.split()
                if len(parts) > 1:
                    target = parts[1].lower()
                    if target == "gemini":
                        api_key = os.getenv("GEMINI_API_KEY")
                        if not api_key or api_key == "your_gemini_api_key_here":
                            print("⚠️ Chưa có GEMINI_API_KEY hợp lệ trong file .env! Vui lòng bổ sung key.")
                        else:
                            provider = GeminiProvider()
                            print(f"✅ Đã chuyển sang Gemini API ({provider.model_name})")
                    elif target == "openai":
                        api_key = os.getenv("OPENAI_API_KEY")
                        if not api_key or api_key == "your_openai_api_key_here":
                            print("⚠️ Chưa có OPENAI_API_KEY hợp lệ trong file .env! Vui lòng bổ sung key.")
                        else:
                            provider = OpenAIProvider()
                            print(f"✅ Đã chuyển sang OpenAI API ({provider.model_name})")
                    elif target == "mock":
                        provider = MockProvider()
                        print("✅ Đã chuyển sang Mock Engine (Offline Mode)")
                    else:
                        print(f"⚠️ Provider '{target}' không hợp lệ. Chọn: gemini | openai | mock")
                continue

            # Run ReAct Agent with the current active provider API
            run_react_agent(user_input, provider)
            print("\n" + "─" * 65 + "\n")

        except (KeyboardInterrupt, EOFError):
            print("\n👋 Đã thoát Terminal Chat.")
            break


if __name__ == "__main__":
    main()
