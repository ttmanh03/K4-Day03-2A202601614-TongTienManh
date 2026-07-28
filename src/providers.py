"""
🔌 MULTI-PROVIDER LLM ADAPTER (OpenAI, Gemini, Anthropic, OpenRouter & Offline Mock)
Hỗ trợ chuyển đổi linh hoạt giữa các nhà cung cấp AI chỉ bằng cách đổi biến môi trường LLM_PROVIDER.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class BaseLLMProvider:
    """Interface cơ sở cho tất cả các LLM Provider"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-2.5-flash"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env!"
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(
                model=self.model_name,
                contents=contents
            )
            return response.text
        except Exception as e:
            return f"[Gemini Exception]: {str(e)}"


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (GPT-4o, GPT-3.5-turbo, etc.)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env!"
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude Provider (Claude 3.5 Sonnet, Claude 3 Haiku)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "claude-3-haiku-20240307"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_anthropic_api_key_here":
            return "[Anthropic Error]: Chưa cấu hình ANTHROPIC_API_KEY trong file .env!"
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            kwargs = {
                "model": self.model_name,
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }
            if system_prompt:
                kwargs["system"] = system_prompt
                
            response = client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as e:
            return f"[Anthropic Exception]: {str(e)}"


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter Provider (Hỗ trợ gọi mọi model qua OpenRouter API)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "google/gemini-2.5-flash"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            return "[OpenRouter Error]: Chưa cấu hình OPENROUTER_API_KEY trong file .env!"
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model_name,
                "messages": messages
            }
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"[OpenRouter API Error {res.status_code}]: {res.text}"
        except Exception as e:
            return f"[OpenRouter Exception]: {str(e)}"


class MockProvider(BaseLLMProvider):
    """Offline Mock Provider — Giả lập ReAct trace cho Cupid Agent (không cần API key)"""

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        text = prompt.lower()
        obs_count = text.count("observation:")

        # TC-1 & TC-2: Câu hỏi tổng quát -> Final Answer ngay
        if "mối quan hệ lành mạnh" in text or "mbti lại quan trọng" in text:
            return (
                "Thought: Đây là câu hỏi tổng quát, trả lời từ kiến thức có sẵn, không cần tool.\n"
                "Final Answer: Một mối quan hệ lành mạnh cần: (1) Tôn trọng lẫn nhau, "
                "(2) Giao tiếp cởi mở và trung thực, (3) Tin tưởng và chung thủy, "
                "(4) Hỗ trợ nhau phát triển, (5) Tôn trọng không gian cá nhân."
            )

        # TC-3: Tương thích cung hoàng đạo Bảo Bình - Thiên Bình -> 1 tool
        if "bảo bình" in text and "thiên bình" in text:
            if obs_count == 0:
                return (
                    'Thought: Cần dữ liệu tương thích cung hoàng đạo, phải gọi tool.\n'
                    'Action: calculate_zodiac_compatibility({"zodiac_1": "Bảo Bình", "zodiac_2": "Thiên Bình"})'
                )
            return (
                "Thought: Đã có kết quả từ tool. Tổng hợp câu trả lời.\n"
                "Final Answer: Bảo Bình và Thiên Bình đạt 95% tương thích — "
                "cùng hệ Khí, giao tiếp cực kỳ ăn ý. Cặp đôi cực kỳ tiềm năng!"
            )

        # TC-4: MBTI INTJ + ENFP -> 2 tools theo thứ tự
        if "intj" in text and "enfp" in text:
            if obs_count == 0:
                return (
                    'Thought: Phân tích MBTI trước, rồi mới gợi ý hẹn hò.\n'
                    'Action: analyze_mbti_match({"mbti_1": "INTJ", "mbti_2": "ENFP"})'
                )
            elif obs_count == 1:
                return (
                    'Thought: INTJ-ENFP hợp nhau 95%. Tiếp theo gợi ý hẹn hò lãng mạn tại Hà Nội.\n'
                    'Action: suggest_date_ideas({"location": "Hà Nội", "budget": "trung bình", "vibe": "lãng mạn"})'
                )
            return (
                "Thought: Đã có đủ Observation từ cả 2 tool. Tổng hợp.\n"
                "Final Answer: INTJ và ENFP là Cặp đôi Kim Cương — 95% tương thích! "
                "Kịch bản hẹn hò lãng mạn tại Hà Nội: Ngắm hoàng hôn Hồ Tây → Ăn tối Pasta tại Trúc Bạch → Đi dạo Phố Cổ."
            )

        # TC-5: Cung bịa đặt + action out-of-scope
        if "thiên mã tọa" in text or "ngân hà tinh" in text:
            if obs_count == 0:
                return (
                    'Thought: Phải gọi tool để kiểm tra, không tự bịa kết quả.\n'
                    'Action: calculate_zodiac_compatibility({"zodiac_1": "Thiên Mã Tọa", "zodiac_2": "Ngân Hà Tinh"})'
                )
            return (
                "Thought: Tool trả fallback vì hai cung không chuẩn. "
                "Yêu cầu đặt nhẫn nằm ngoài phạm vi hệ thống — tôi không có tool này.\n"
                "Final Answer: 'Thiên Mã Tọa' và 'Ngân Hà Tinh' không phải cung hoàng đạo hợp lệ. "
                "Vui lòng cung cấp cung đúng (ví dụ: Bảo Bình, Sư Tử…). "
                "Tôi không thể đặt nhẫn đính hôn — đó là quyết định của con người 💍"
            )

        # Fallback chung
        return (
            "Thought: Câu hỏi tổng quát, không cần gọi tool.\n"
            "Final Answer: 🤖 Tôi là Cupid Agent! Hỏi tôi về độ tương thích "
            "cung hoàng đạo, MBTI hoặc gợi ý hẹn hò nhé!"
        )


def get_llm_provider(provider_name: str = None) -> BaseLLMProvider:
    """Factory function tự chọn Provider từ biến môi trường LLM_PROVIDER"""
    name = (provider_name or os.getenv("LLM_PROVIDER") or "mock").lower().strip()
    
    if name == "gemini":
        return GeminiProvider()
    elif name == "openai":
        return OpenAIProvider()
    elif name == "anthropic":
        return AnthropicProvider()
    elif name == "openrouter":
        return OpenRouterProvider()
    else:
        return MockProvider()


if __name__ == "__main__":
    print("=== TEST MULTI-PROVIDER LLM ADAPTER ===")
    provider = get_llm_provider()
    print(f"✅ Provider đang dùng: {provider.__class__.__name__}")
    print(f"🤖 User Query: Hello")
    print(f"💬 Response  : {provider.generate('Hello')}")
