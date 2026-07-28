"""
Kiểm chứng 4 cấp độ AI hoạt động ĐÚNG VAI TRÒ của mình (không chỉ "có trả lời").

Chạy khi backend đang bật (python backend/run.py):
    python backend/verify_levels.py

Mỗi cấp độ được kiểm bằng đặc trưng phân biệt nó với cấp khác:
  Cấp 1: KHÔNG gọi LLM  -> deterministic, cực nhanh, có fallback khi không khớp luật
  Cấp 2: CÓ gọi LLM nhưng KHÔNG gọi tool -> không có dữ liệu từ tool trong câu trả lời
  Cấp 3: CÓ gọi tool    -> Thought/Action/Observation, Observation khớp output tool thật
  Cấp 4: TỰ lập kế hoạch -> có plan trước, có Memory, có Self-Evaluation
"""

import json
import os
import sys
import time
import urllib.request

# Đảm bảo in Tiếng Việt không lỗi trên Windows Console
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

BASE = "http://127.0.0.1:8001"

passed = 0
failed = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {label}")
    else:
        failed += 1
        print(f"  [FAIL] {label}" + (f"\n         -> {detail}" if detail else ""))


# Mỗi lần chạy dùng session riêng để bộ nhớ của lần chạy trước không làm sai kết quả.
SESSION = f"verify-{int(time.time())}"


def post_json(path: str, query: str) -> dict:
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps({"query": query, "session_id": SESSION}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as res:
        return json.loads(res.read())


def post_sse(path: str, query: str) -> list[dict]:
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps({"query": query, "session_id": SESSION}).encode(),
        headers={"Content-Type": "application/json"},
    )
    events = []
    with urllib.request.urlopen(req, timeout=180) as res:
        for raw in res:
            line = raw.decode("utf-8").strip()
            if line.startswith("data:"):
                events.append(json.loads(line[5:].strip()))
    return events


def get_memory() -> dict:
    with urllib.request.urlopen(f"{BASE}/api/memory/{SESSION}", timeout=30) as res:
        return json.loads(res.read())


ZODIAC_Q = "Bảo Bình và Thiên Bình có hợp nhau không?"
MULTI_Q = (
    "Tôi là INTJ và người ấy là ENFP, cùng ở Hà Nội. "
    "Phân tích độ hợp rồi gợi ý buổi hẹn lãng mạn ngân sách trung bình."
)

# ---------------------------------------------------------------- CẤP 1
print("\n=== CẤP 1: RULE-BASED BOT (không LLM, khớp từ khóa) ===")

t0 = time.perf_counter()
r1a = post_json("/api/chat/level1", ZODIAC_Q)["response"]
elapsed = time.perf_counter() - t0
r1b = post_json("/api/chat/level1", ZODIAC_Q)["response"]

check("Trả lời tức thì (<0.5s) => không thể có API call tới LLM", elapsed < 0.5, f"mất {elapsed:.3f}s")
check("Deterministic: 2 lần hỏi giống hệt nhau (LLM thì không thể)", r1a == r1b)
check("Khớp đúng luật 'cung hoàng đạo'", "cung hoàng đạo" in r1a.lower())
check(
    "KHÔNG chứa dữ liệu tool (95%, hệ Khí) => không gọi tool",
    "95%" not in r1a and "hệ Khí" not in r1a,
    r1a[:120],
)

r1_unknown = post_json("/api/chat/level1", "Giải thích thuyết tương đối hẹp giúp tôi")
check(
    "Câu không khớp luật nào => rơi vào fallback",
    r1_unknown.get("matched_rule") == "fallback",
    f"matched_rule={r1_unknown.get('matched_rule')} | {r1_unknown['response'][:100]}",
)

# ---------------------------------------------------------------- CẤP 2
print("\n=== CẤP 2: LLM CHATBOT (có LLM, KHÔNG tool) ===")

r2 = post_json("/api/chat/baseline", ZODIAC_Q)["response"]

check("Có trả lời thực chất (>150 ký tự)", len(r2) > 150, f"{len(r2)} ký tự")
check("Không phải câu fallback cứng của Cấp 1", "ngoài tập luật" not in r2)
check(
    "KHÔNG chứa chuỗi output đặc trưng của tool => không gọi tool",
    "Kết quả phân tích Cung Hoàng Đạo" not in r2,
    r2[:150],
)
check(
    "Không sinh Thought/Action (đúng vai chatbot thuần)",
    "Action:" not in r2 and "Thought:" not in r2,
)

# ---------------------------------------------------------------- CẤP 3
print("\n=== CẤP 3: REACTIVE AGENT (Thought -> Action -> Observation) ===")

ev3 = post_sse("/api/chat/react", ZODIAC_Q)
types3 = [e["type"] for e in ev3]

check("Có bước Thought", "thought" in types3, str(types3))
check("Có bước Action (gọi tool)", "action" in types3, str(types3))
check("Có bước Observation", "observation" in types3, str(types3))
check("Thought xuất hiện TRƯỚC Action", types3.index("thought") < types3.index("action"))
check(
    "Mỗi Observation đứng ngay sau một Action (đúng chuẩn ReAct)",
    all(types3[i - 1] == "action" for i, t in enumerate(types3) if t == "observation"),
    str(types3),
)
check(
    "Kết thúc bằng Final Answer, KHÔNG rơi guardrail oan",
    types3[-1] == "final",
    f"kết thúc bằng '{types3[-1]}' — chuỗi: {types3}",
)
check(
    "Không lãng phí vòng lặp (<= 3 lượt LLM cho câu 1-tool)",
    max(e["step"] for e in ev3) <= 3,
    f"dùng {max(e['step'] for e in ev3)} bước",
)

actions3 = [e for e in ev3 if e["type"] == "action"]
from tools import AVAILABLE_TOOLS, calculate_zodiac_compatibility  # noqa: E402

check(
    "Tool được gọi là tool có thật trong AVAILABLE_TOOLS",
    all(a["tool"] in AVAILABLE_TOOLS for a in actions3),
    str([a["tool"] for a in actions3]),
)

obs3 = [e["content"] for e in ev3 if e["type"] == "observation"]
truth = calculate_zodiac_compatibility("Bảo Bình", "Thiên Bình")
check(
    "Observation KHỚP CHÍNH XÁC output tool gọi trực tiếp (grounding, không bịa)",
    any(o == truth for o in obs3),
    f"tool thật trả: {truth[:80]}... | agent nhận: {obs3[0][:80] if obs3 else 'N/A'}...",
)

final3 = [e["content"] for e in ev3 if e["type"] == "final"]
check(
    "Final Answer dùng số liệu từ Observation (95%)",
    bool(final3) and "95" in final3[0],
    final3[0][:150] if final3 else "không có final",
)

# ---------------------------------------------------------------- CẤP 4
print("\n=== CẤP 4: AUTONOMOUS AGENT (Planning + Memory + Self-Evaluation) ===")

ev4 = post_sse("/api/chat/autonomous", MULTI_Q)
types4 = [e["type"] for e in ev4]

check("Có bước Planning (tự rã mục tiêu)", "plan" in types4, str(types4))
check("Planning là bước ĐẦU TIÊN", types4[0] == "plan", str(types4[:3]))
check("Có Memory (lưu vết từng bước)", "memory" in types4, str(types4))
check("Có Self-Evaluation (tự đánh giá)", "evaluation" in types4, str(types4))
check("Có Final Answer", "final" in types4, str(types4))

plan4 = [e["content"] for e in ev4 if e["type"] == "plan"][0]
subtasks = [ln for ln in plan4.splitlines() if ln.strip()]
check("Kế hoạch chia thành nhiều nhiệm vụ con (>=2)", len(subtasks) >= 2, plan4)

mem4 = [e for e in ev4 if e["type"] == "memory"]
check(
    "Số lần lưu Memory khớp số nhiệm vụ con",
    len(mem4) == len(subtasks),
    f"{len(mem4)} memory / {len(subtasks)} nhiệm vụ",
)
check(
    "Self-Evaluation diễn ra SAU khi đã lưu Memory",
    types4.index("evaluation") > max(i for i, t in enumerate(types4) if t == "memory"),
)
check(
    "Cấp 4 có bước mà Cấp 3 KHÔNG có (plan/memory/evaluation)",
    {"plan", "memory", "evaluation"}.isdisjoint(set(types3)),
    f"Cấp 3 có: {sorted(set(types3))}",
)

# ---------------------------------------------------- MEMORY CHỈ THUỘC CẤP 4
print("\n=== MEMORY LÀ ĐẶC TRƯNG RIÊNG CỦA CẤP 4 ===")

mem = get_memory()
check(
    "Sau khi chạy đủ 4 cấp, memory chỉ ghi lại lượt của Cấp 4",
    len(mem["short_term"]) == 1,
    f"{len(mem['short_term'])} lượt được lưu — Cấp 2/3 không được phép ghi memory",
)
check(
    "Lượt được lưu đúng là câu hỏi của Cấp 4",
    bool(mem["short_term"]) and mem["short_term"][0]["user"] == MULTI_Q,
    str([t["user"][:50] for t in mem["short_term"]]),
)

# --------------------------------------- KHÔNG RÒ RỈ CHI TIẾT HỆ THỐNG
print("\n=== CÂU TRẢ LỜI KHÔNG ĐƯỢC LỘ CHI TIẾT HỆ THỐNG ===")

LEAKS = [
    "analyze_mbti_match",
    "calculate_zodiac_compatibility",
    "suggest_date_ideas",
    "observation",
    "system prompt",
    "tập luật",
    "keyword",
    "baseline",
    "theo tool",
    "tool trả về",
    "dựa trên tool",
]

for label, text in [
    ("Cấp 1", r1a),
    ("Cấp 1 (fallback)", r1_unknown["response"]),
    ("Cấp 2", r2),
    ("Cấp 3", final3[0] if final3 else ""),
    ("Cấp 4", [e["content"] for e in ev4 if e["type"] == "final"][0]),
]:
    hits = [kw for kw in LEAKS if kw in text.lower()]
    check(f"{label}: không lộ tên tool / cơ chế nội bộ", not hits, f"lộ {hits} | {text[:180]}")

# ---------------------------------------------------------------- KẾT LUẬN
print("\n" + "=" * 60)
print(f"KẾT QUẢ: {passed} PASS · {failed} FAIL")
print("=" * 60)
sys.exit(1 if failed else 0)
