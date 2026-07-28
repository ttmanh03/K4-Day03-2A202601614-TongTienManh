"""
🔌 MULTI-PROVIDER LLM ADAPTER (OpenAI, Gemini, Anthropic, OpenRouter & Offline Mock)
Hỗ trợ chuyển đổi linh hoạt giữa các nhà cung cấp AI chỉ bằng cách đổi biến môi trường LLM_PROVIDER.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class BaseLLMProvider:
    """Interface cơ sở cho tất cả các LLM Provider"""

    # Usage của lần generate() gần nhất, dạng dict hoặc None nếu provider không
    # trả về. Khai báo ở class level để mọi subclass có sẵn thuộc tính này mà
    # không phải sửa __init__ của chúng.
    last_usage = None

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError

    def _record_usage(self, usage) -> None:
        """
        Chuẩn hoá object usage của từng SDK về một dict chung.

        Mỗi nhà cung cấp đặt tên field khác nhau:
        OpenAI/DeepSeek/OpenRouter -> prompt_tokens / completion_tokens
        Anthropic                  -> input_tokens / output_tokens
        Gemini                     -> prompt_token_count / candidates_token_count
        """
        if usage is None:
            self.last_usage = None
            return

        def pick(*names):
            for n in names:
                # OpenRouter trả JSON đã parse thành dict, các SDK khác trả object.
                v = usage.get(n) if isinstance(usage, dict) else getattr(usage, n, None)
                if v is not None:
                    return v
            return 0

        prompt_t = pick("prompt_tokens", "input_tokens", "prompt_token_count")
        completion_t = pick("completion_tokens", "output_tokens", "candidates_token_count")
        self.last_usage = {
            "prompt_tokens": prompt_t,
            "completion_tokens": completion_t,
            "total_tokens": prompt_t + completion_t,
        }


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
            self._record_usage(getattr(response, "usage_metadata", None))
            return response.text
        except Exception as e:
            self.last_usage = None
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
            self._record_usage(getattr(response, "usage", None))
            return response.choices[0].message.content
        except Exception as e:
            self.last_usage = None
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
            self._record_usage(getattr(response, "usage", None))
            return response.content[0].text
        except Exception as e:
            self.last_usage = None
            return f"[Anthropic Exception]: {str(e)}"


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek Provider (API tương thích chuẩn OpenAI, đổi base_url)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        # deepseek-chat/deepseek-reasoner (alias cũ) đã bị khai tử từ 24/07/2026.
        # Model hiện hành: deepseek-v4-flash (nhanh, rẻ) hoặc deepseek-v4-pro (reasoning).
        self.model_name = model or os.getenv("LLM_MODEL") or "deepseek-v4-flash"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_deepseek_api_key_here":
            return "[DeepSeek Error]: Chưa cấu hình DEEPSEEK_API_KEY trong file .env!"
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            self._record_usage(getattr(response, "usage", None))
            return response.choices[0].message.content
        except Exception as e:
            self.last_usage = None
            return f"[DeepSeek Exception]: {str(e)}"


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
                self._record_usage(data.get("usage"))
                return data["choices"][0]["message"]["content"]
            else:
                self.last_usage = None
                return f"[OpenRouter API Error {res.status_code}]: {res.text}"
        except Exception as e:
            self.last_usage = None
            return f"[OpenRouter Exception]: {str(e)}"


class MockProvider(BaseLLMProvider):
    """Offline Mock Provider — Giả lập phản hồi cho Cupid Agent (không cần API key).
    
    Hỗ trợ 2 chế độ:
    - mode='baseline': trả lời plain text như Chatbot thực sự (không có Thought/Action)
    - mode='agent' (mặc định): trả Thought -> Action -> Final Answer theo luồng ReAct
    
    Chế độ được chọn qua tham số system_prompt: nếu system_prompt chứa chuỗi
    'BASELINE KHÔNG CÓ TOOL' thì mock trả lời kiểu chatbot.
    """

    def _is_baseline(self, system_prompt: str) -> bool:
        """Kiểm tra xem lệnh gọi này là baseline hay agent dựa vào system_prompt."""
        return "BASELINE KHÔNG CÓ TOOL" in system_prompt

    def _mock_baseline(self, text: str) -> str:
        """Phản hồi plain text cho Chatbot Baseline — không có Thought/Action."""
        if "mối quan hệ lành mạnh" in text:
            return (
                "Một mối quan hệ lành mạnh và bền vững cần: (1) Tôn trọng lẫn nhau, "
                "(2) Giao tiếp cởi mở và trung thực, (3) Tin tưởng và chung thủy, "
                "(4) Hỗ trợ nhau phát triển bản thân, (5) Tôn trọng không gian cá nhân. "
                "Đây là những nền tảng cốt lõi mà bất kỳ mối quan hệ nào cũng cần có."
            )
        if "mbti lại quan trọng" in text:
            return (
                "MBTI được nhiều người dùng vì nó cung cấp ngôn ngữ chung để hiểu "
                "phong cách giao tiếp và xử lý cảm xúc của nhau. Tuy nhiên, mình xin lưu ý: "
                "MBTI chỉ là công cụ tham khảo, không phải định mệnh — hai người "
                "với bất kỳ loại tính cách nào đều có thể xây dựng mối quan hệ tốt "
                "nếu cùng cố gắng thấu hiểu và tôn trọng nhau."
            )
        if "bảo bình" in text and "thiên bình" in text:
            return (
                "Bảo Bình và Thiên Bình thường được xem là cặp tương thích khá tốt vì "
                "cả hai đều thuộc nhóm Khí và đề cao tư duy lý trí. Tuy nhiên mình không "
                "có công cụ tra cứu để cho bạn con số cụ thể — đây chỉ là nhận xét tổng quát."
            )
        if "intj" in text and "enfp" in text:
            return (
                "INTJ và ENFP là cặp tính cách đối cực nhau theo nhiều chiều, và điều đó "
                "có thể tạo ra sức hút đáng kể. Tuy nhiên, mình không thể xác minh mức độ "
                "tương thích bằng dữ liệu công cụ — chỉ có thể nói rằng sự bổ trợ giữa "
                "lý trí (INTJ) và cảm hứng (ENFP) có tiềm năng tốt nếu cả hai chịu thấu hiểu nhau. "
                "Về gợi ý hẹn hò, bạn có thể thử cà phê yên tĩnh, tham quan bảo tàng "
                "hoặc đi dạo bờ hồ tại Hà Nội."
            )
        if "thiên mã tọa" in text or "ngân hà tinh" in text:
            return (
                "'Thiên Mã Tọa' và 'Ngân Hà Tinh' không phải cung hoàng đạo tiêu chuẩn, "
                "nên mình không thể phân tích tương thích. Và dù kết quả thế nào, "
                "mình cũng không thể đặt nhẫn đính hôn — đó là quyết định thuộc về con người, "
                "không phải chatbot."
            )
        return (
            "Chào bạn! Mình là Cupid Chatbot — sẵn sàng tư vấn tình cảm và "
            "độ tương thích ở mức kiến thức tổng quát. Bạn muốn hỏi về điều gì?"
        )

    def _mock_agent(self, text: str) -> str:
        """Phản hồi Thought -> Action / Final Answer cho ReAct Agent."""
        obs_count = text.count("observation:")

        # TC-1 & TC-2: Câu hỏi tổng quát -> Final Answer ngay
        if "mối quan hệ lành mạnh" in text or "mbti lại quan trọng" in text:
            return (
                "Thought: Đây là câu hỏi tổng quát, không cần gọi tool.\n"
                "Final Answer: Một mối quan hệ lành mạnh cần: (1) Tôn trọng lẫn nhau, "
                "(2) Giao tiếp cởi mở và trung thực, (3) Tin tưởng và chung thủy, "
                "(4) Hỗ trợ nhau phát triển, (5) Tôn trọng không gian cá nhân."
            )

        # TC-3: Tương thích cung hoàng đạo Bảo Bình - Thiên Bình
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

        # TC-4: MBTI INTJ + ENFP -> 2 tools theo thứ tự bắt buộc
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
                "Kịch bản hẹn hò lãng mạn tại Hà Nội: Ngắm hoàng hôn Hồ Tây → "
                "Ăn tối Pasta/Steak tại Trúc Bạch → Đi dạo Phố Cổ."
            )

        # TC-5: Cung bịa đặt + action out-of-scope
        if "thiên mã tọa" in text or "ngân hà tinh" in text:
            if obs_count == 0:
                return (
                    'Thought: Phải gọi tool để kiểm tra dữ liệu, không tự bịa kết quả.\n'
                    'Action: calculate_zodiac_compatibility({"zodiac_1": "Thiên Mã Tọa", "zodiac_2": "Ngân Hà Tinh"})'
                )
            return (
                "Thought: Tool trả kết quả fallback vì hai cung không chuẩn. "
                "Yêu cầu đặt nhẫn nằm ngoài phạm vi hệ thống — không có tool này.\n"
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

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        text = prompt.lower()
        if self._is_baseline(system_prompt):
            return self._mock_baseline(text)
        return self._mock_agent(text)


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
    elif name == "deepseek":
        return DeepSeekProvider()
    else:
        return MockProvider()


if __name__ == "__main__":
    print("=== TEST MULTI-PROVIDER LLM ADAPTER ===")
    provider = get_llm_provider()
    print(f"✅ Provider đang dùng: {provider.__class__.__name__}")
    print(f"🤖 User Query: Hello")
    print(f"💬 Response  : {provider.generate('Hello')}")
