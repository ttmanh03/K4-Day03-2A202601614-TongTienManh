"""
Cấp độ 1 (Rule-Based Bot) và Cấp độ 4 (Autonomous Agent) cho Cupid Agent.

Cấp 2 (LLM Chatbot) và Cấp 3 (ReAct Agent) nằm ở agent_runner.py.

Lưu ý: src/ai_levels/*.py là script demo boilerplate gốc (chủ đề thời tiết/
vé máy bay, hard-code sẵn kịch bản) nên không tái sử dụng được cho Cupid.
Hai cấp độ ở đây được viết lại theo đúng domain ghép đôi/tương thích.
"""

import json
import re

from agent_runner import _call_tool, _parse_action
from tools import AVAILABLE_TOOLS

# ---------------------------------------------------------------------------
# CẤP ĐỘ 1: RULE-BASED BOT (khớp từ khóa if/else, KHÔNG dùng LLM)
# ---------------------------------------------------------------------------

RULES = [
    (
        ("chào", "hello", "hi ", "xin chào"),
        "Xin chào! Tôi là Cupid Rule-Based Bot (Cấp độ 1). Tôi chỉ biết khớp từ khóa cố định thôi!",
    ),
    (
        ("cung hoàng đạo", "bảo bình", "thiên bình", "kim ngưu", "sư tử", "xử nữ", "bọ cạp"),
        "Tôi thấy bạn nhắc tới cung hoàng đạo, nhưng tôi là bot luật cố định — tôi không tra cứu "
        "được bảng tương thích. Hãy thử Cấp độ 3 (ReAct Agent) để tôi gọi tool thật!",
    ),
    (
        ("mbti", "intj", "enfp", "infj", "entp", "istj", "esfp"),
        "Từ khóa MBTI đã khớp luật! Nhưng tôi chỉ trả lời câu có sẵn: MBTI gồm 16 nhóm tính cách. "
        "Tôi không phân tích được độ hợp của 2 người cụ thể.",
    ),
    (
        ("hẹn hò", "đi chơi", "date", "quán"),
        "Gợi ý cố định: đi cà phê, ăn tối, đi dạo. Tôi không cá nhân hóa được theo địa điểm/ngân sách "
        "vì tôi không có công cụ nào cả.",
    ),
    (
        ("liên hệ", "hotline", "hỗ trợ"),
        "Hotline hỗ trợ: 1900-1234 · Email: support@vinuni.edu.vn",
    ),
]

FALLBACK = (
    "Xin lỗi, câu hỏi của bạn nằm ngoài tập luật (keywords) được cài sẵn! "
    "Đây chính là giới hạn lớn nhất của Cấp độ 1: không có luật nào khớp thì bot bó tay."
)


def run_rule_based(user_query: str) -> str:
    """Cấp độ 1: chỉ khớp từ khóa, không LLM, không tool. Luôn trả lời tức thì."""
    text = user_query.lower()
    for keywords, answer in RULES:
        if any(k in text for k in keywords):
            return answer
    return FALLBACK


# ---------------------------------------------------------------------------
# CẤP ĐỘ 4: AUTONOMOUS AGENT (Planning + Memory + Self-Evaluation)
# ---------------------------------------------------------------------------

MAX_SUBTASKS = 3

PLANNER_PROMPT = """Bạn là Cupid Autonomous Agent — bạn TỰ RÃ mục tiêu người dùng thành các bước nhỏ.

CÁC TOOL CÓ SẴN:
1. calculate_zodiac_compatibility({"zodiac_1": str, "zodiac_2": str})
2. analyze_mbti_match({"mbti_1": str, "mbti_2": str})
3. suggest_date_ideas({"location": str, "budget": str, "vibe": str})

Hãy chia mục tiêu của người dùng thành tối đa %d nhiệm vụ con theo thứ tự hợp lý.
CHỈ trả về JSON array các chuỗi, không giải thích gì thêm. Ví dụ:
["Phân tích độ hợp MBTI giữa INTJ và ENFP", "Gợi ý buổi hẹn lãng mạn ở Hà Nội"]
""" % MAX_SUBTASKS

EXECUTOR_PROMPT = """Bạn là Cupid Autonomous Agent đang thực hiện MỘT nhiệm vụ con.

CÁC TOOL HỢP LỆ:
1. calculate_zodiac_compatibility({"zodiac_1": str, "zodiac_2": str})
2. analyze_mbti_match({"mbti_1": str, "mbti_2": str})
3. suggest_date_ideas({"location": str, "budget": str, "vibe": str})

Nếu nhiệm vụ cần dữ liệu từ tool, trả về đúng 1 dòng:
Action: <tool_name>(<JSON object>)

Nếu nhiệm vụ KHÔNG cần tool (chỉ suy luận/tổng hợp), trả về:
Result: <kết quả ngắn gọn>

Không giải thích thêm ngoài 2 định dạng trên."""

EVALUATOR_PROMPT = """Bạn là Cupid Autonomous Agent đang TỰ ĐÁNH GIÁ kết quả của chính mình.

Dựa trên mục tiêu ban đầu và bộ nhớ (memory) các bước đã làm, hãy:
1. Nhận xét ngắn gọn đã hoàn thành mục tiêu chưa (1-2 câu).
2. Sau đó xuống dòng và viết "Final Answer:" rồi tổng hợp câu trả lời hoàn chỉnh cho người dùng.

Chỉ dùng dữ liệu có trong memory, KHÔNG bịa thêm số liệu."""


def _parse_plan(raw: str) -> list[str]:
    """Trích JSON array kế hoạch từ output LLM. Fallback: tách theo dòng."""
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        try:
            plan = json.loads(match.group(0))
            if isinstance(plan, list):
                return [str(p) for p in plan if str(p).strip()][:MAX_SUBTASKS]
        except json.JSONDecodeError:
            pass

    lines = [re.sub(r"^\s*[-*\d.)\s]+", "", ln).strip() for ln in raw.splitlines()]
    return [ln for ln in lines if ln][:MAX_SUBTASKS]


def stream_autonomous_agent(user_query: str, provider):
    """
    Generator yield từng bước của Autonomous Agent (Cấp độ 4).

    Khác Cấp độ 3 ở chỗ: agent TỰ lập kế hoạch trước (planning), lưu kết quả
    từng bước vào memory, rồi TỰ đánh giá xem đã đạt mục tiêu chưa.

    Các loại step: "plan" | "thought" | "action" | "observation" | "memory"
                   | "evaluation" | "final" | "error"
    """
    # --- 1. PLANNING: agent tự rã mục tiêu ---
    try:
        raw_plan = provider.generate(f"Mục tiêu của người dùng: {user_query}", system_prompt=PLANNER_PROMPT)
    except Exception as e:
        yield {"type": "error", "step": 1, "content": f"Lỗi khi lập kế hoạch: {e}"}
        return

    subtasks = _parse_plan(raw_plan)
    if not subtasks:
        yield {"type": "error", "step": 1, "content": "Không lập được kế hoạch từ mục tiêu này."}
        return

    yield {"type": "plan", "step": 1, "content": "\n".join(f"{i}. {t}" for i, t in enumerate(subtasks, 1))}

    # --- 2. EXECUTION: chạy từng nhiệm vụ con, lưu memory ---
    memory: list[dict] = []
    executed_actions: set = set()
    step = 1

    for idx, task in enumerate(subtasks, 1):
        step += 1
        yield {"type": "thought", "step": step, "content": f"Nhiệm vụ {idx}/{len(subtasks)}: {task}"}

        context = f"Mục tiêu tổng: {user_query}\nNhiệm vụ con cần làm: {task}\n"
        if memory:
            context += "Kết quả các bước trước:\n" + "\n".join(
                f"- {m['task']}: {m['result']}" for m in memory
            )

        try:
            llm_output = provider.generate(context, system_prompt=EXECUTOR_PROMPT)
        except Exception as e:
            yield {"type": "error", "step": step, "content": f"Lỗi khi thực thi nhiệm vụ: {e}"}
            return

        tool_name, kwargs = _parse_action(llm_output)
        if tool_name and tool_name in AVAILABLE_TOOLS:
            yield {"type": "action", "step": step, "tool": tool_name, "args": kwargs}
            result = _call_tool(tool_name, kwargs or {}, executed_actions)
            yield {"type": "observation", "step": step, "content": result}
        else:
            match = re.search(r"Result:\s*(.+)", llm_output, re.DOTALL)
            result = match.group(1).strip() if match else llm_output.strip()
            yield {"type": "observation", "step": step, "content": result}

        memory.append({"task": task, "result": result})
        yield {
            "type": "memory",
            "step": step,
            "content": f"Đã lưu {len(memory)}/{len(subtasks)} kết quả vào bộ nhớ.",
        }

    # --- 3. SELF-EVALUATION + tổng hợp ---
    step += 1
    memory_dump = "\n".join(f"- {m['task']}\n  → {m['result']}" for m in memory)
    eval_context = f"Mục tiêu ban đầu: {user_query}\n\nMemory:\n{memory_dump}"

    try:
        raw_eval = provider.generate(eval_context, system_prompt=EVALUATOR_PROMPT)
    except Exception as e:
        yield {"type": "error", "step": step, "content": f"Lỗi khi tự đánh giá: {e}"}
        return

    if "Final Answer:" in raw_eval:
        idx = raw_eval.index("Final Answer:")
        assessment = raw_eval[:idx].strip()
        final = raw_eval[idx + len("Final Answer:"):].strip()
    else:
        assessment = "Đã tổng hợp xong toàn bộ nhiệm vụ con."
        final = raw_eval.strip()

    if assessment:
        yield {"type": "evaluation", "step": step, "content": assessment}
    yield {"type": "final", "step": step + 1, "content": final}
