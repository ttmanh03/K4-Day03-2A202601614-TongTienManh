"""
🚀 CẤP ĐỘ 4: AUTONOMOUS AGENT (Planning, Working Memory & Self-Reflection)
Tự rã mục tiêu (Goal Decomposition), lưu bộ nhớ (Memory), thực thi công cụ và Tự đánh giá (Self-Evaluation).
"""

import json
import os
import sys

# Ensure src/ is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import AVAILABLE_TOOLS
from providers import get_llm_provider


class AutonomousAgent:
    """
    Autonomous Agent Cấp 4:
    - Phase 1: Planning (Chia nhỏ mục tiêu lớn thành các sub-task)
    - Phase 2: Action Execution & Working Memory Storage
    - Phase 3: Self-Reflection & Evaluation (Tự kiểm tra ràng buộc)
    - Phase 4: Final Synthesis (Tổng hợp lời khuyên hoàn chỉnh)
    """

    def __init__(self, provider=None):
        self.provider = provider or get_llm_provider()
        self.memory = []  # Bộ nhớ lưu vết quá trình thực thi

    def plan_goal(self, high_level_goal: str) -> list:
        """Phase 1: Planning - LLM tự chia nhỏ mục tiêu phức tạp"""
        plan_prompt = f"""
Bạn là AI Planner cấp 4. Hãy chia nhỏ mục tiêu sau thành đúng 3 bước thực thi cụ thể:
Mục tiêu: "{high_level_goal}"

Trả về định dạng JSON Array chứa 3 chuỗi công việc. Ví dụ:
["Bước 1: Phân tích độ hợp MBTI/Zodiac", "Bước 2: Tìm kịch bản hẹn hò", "Bước 3: Tổng hợp và đánh giá ràng buộc"]
"""
        output = self.provider.generate(high_level_goal, system_prompt=plan_prompt)
        try:
            # Parse JSON plan list
            import re
            m = re.search(r'\[.*\]', output, re.DOTALL)
            if m:
                return json.loads(m.group(0))
        except Exception:
            pass

        # Fallback plan nếu không parse được JSON
        return [
            "Bước 1: Phân tích độ hợp tính cách & cung hoàng đạo",
            "Bước 2: Tra cứu kịch bản hẹn hò phù hợp với ngân sách & địa điểm",
            "Bước 3: Đánh giá ràng buộc an toàn và tổng hợp kế hoạch"
        ]

    def execute_subtask(self, subtask: str, context: str) -> str:
        """Phase 2: Execution & Tool Execution"""
        text = subtask.lower()
        if "mbti" in text or "tính cách" in text or "intj" in text:
            fn = AVAILABLE_TOOLS["analyze_mbti_match"]
            res = fn(mbti_1="INTJ", mbti_2="ENFP")
            return f"[Tool analyze_mbti_match]: {res}"

        if "cung" in text or "zodiac" in text or "bảo bình" in text:
            fn = AVAILABLE_TOOLS["calculate_zodiac_compatibility"]
            res = fn(zodiac_1="Bảo Bình", zodiac_2="Thiên Bình")
            return f"[Tool calculate_zodiac_compatibility]: {res}"

        if "hẹn hò" in text or "kịch bản" in text or "hà nội" in text:
            fn = AVAILABLE_TOOLS["suggest_date_ideas"]
            res = fn(location="Hà Nội", budget="trung bình", vibe="lãng mạn")
            return f"[Tool suggest_date_ideas]: {res}"

        # LLM reasoning cho subtask chung
        prompt = f"Thực thi công việc: {subtask}\nContext hiện tại: {context}"
        return self.provider.generate(prompt, system_prompt="Bạn là Subtask Executor.")

    def self_reflect(self, goal: str, memory_logs: list) -> str:
        """Phase 3: Self-Reflection & Evaluation - Tự đánh giá kết quả trước khi chốt"""
        logs_str = json.dumps(memory_logs, ensure_ascii=False, indent=2)
        reflection_prompt = f"""
Bạn là AI Inspector cấp 4. Hãy tự đánh giá (Self-Reflection) xem quá trình thực thi có đáp ứng đủ mục tiêu: "{goal}" hay chưa.
Nhật ký bộ nhớ (Memory Logs):
{logs_str}

Hãy đưa ra đánh giá ngắn gọn: (1) Đã đạt mục tiêu chưa? (2) Có vi phạm ràng buộc an toàn/ngân sách không?
"""
        return self.provider.generate(goal, system_prompt=reflection_prompt)

    def run_autonomous_flow(self, high_level_goal: str):
        """Thực thi toàn bộ quy trình Autonomous Agent Cấp 4"""
        print(f"🚀 === [CẤP ĐỘ 4: AUTONOMOUS AGENT] ===")
        print(f"🎯 High-Level Goal: {high_level_goal}\n")

        # 1. Planning
        print("🧠 [Phase 1: Planning] LLM đang rã mục tiêu...")
        plans = self.plan_goal(high_level_goal)
        for i, p in enumerate(plans, 1):
            print(f"   └─ Sub-goal {i}: {p}")

        # 2. Execution & Memory Logging
        print("\n⚙️ [Phase 2: Execution & Working Memory]")
        context = ""
        for i, task in enumerate(plans, 1):
            result = self.execute_subtask(task, context)
            memory_entry = {"subtask": task, "result": result}
            self.memory.append(memory_entry)
            context += f"\n- {task}: {result}"
            print(f"   [Step {i}] {task}")
            print(f"   👁️ Observation/Result: {result}")
            print(f"   💾 Saved to Memory Buffer ({len(self.memory)} items in memory)\n")

        # 3. Self-Reflection
        print("🔍 [Phase 3: Self-Reflection & Evaluation]")
        reflection = self.self_reflect(high_level_goal, self.memory)
        print(f"   🤔 Self-Evaluation: {reflection.strip()}\n")

        # 4. Final Synthesis
        print("🏁 [Phase 4: Final Synthesis]")
        synthesis_prompt = f"""
Dựa vào bộ nhớ thực thi và kết quả tự đánh giá:
Context: {context}
Reflection: {reflection}

Hãy đưa ra câu trả lời hoàn chỉnh, cấu trúc đẹp cho người dùng.
"""
        final_answer = self.provider.generate(high_level_goal, system_prompt=synthesis_prompt)
        print(f"🤖 Autonomous Agent Final Report:\n{final_answer.strip()}")


if __name__ == "__main__":
    agent = AutonomousAgent()
    query = "Tôi muốn kiểm tra độ tương thích giữa INTJ và ENFP, sau đó lên kế hoạch hẹn hò lãng mạn tại Hà Nội với ngân sách trung bình."
    agent.run_autonomous_flow(query)
