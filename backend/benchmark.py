"""
📊 BENCHMARK TELEMETRY — đo latency, token và cost cho báo cáo nhóm.

Chạy đủ bộ test case trong config/test_cases.json qua CẢ HAI nhánh
(Chatbot Baseline và ReAct Agent), đo từng lượt gọi LLM rồi xuất:

- Latency P50 / P99 theo từng task
- Token trung bình mỗi task (đọc `provider.last_usage` do providers.py ghi lại)
- Tổng chi phí ước tính theo đơn giá model
- Tool đã gọi so với `tools_required` của test case -> success rate

Kết quả ghi ra logs/benchmark_<timestamp>.json để báo cáo trích số, và in
bảng tóm tắt Markdown dán thẳng vào report.

Cách chạy:
    python backend/benchmark.py
"""

import json
import os
import statistics
import sys
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import app as cupid_app  # noqa: E402  (phải chỉnh sys.path trước khi import)
from providers import get_llm_provider  # noqa: E402

# Đơn giá USD / 1 triệu token. Chỉnh lại nếu đổi model.
PRICING = {
    "deepseek-v4-flash": {"input": 0.028, "output": 0.042},
    "gpt-4o-mini": {"input": 0.150, "output": 0.600},
    "gemini-2.5-flash": {"input": 0.075, "output": 0.300},
}
DEFAULT_PRICE = {"input": 0.0, "output": 0.0}


class MeteredProvider:
    """
    Bọc provider thật để đếm mọi lượt gọi LLM.

    Không sửa provider gốc — chỉ chặn ở giữa để cộng dồn token và thời gian,
    nên vòng lặp ReAct trong src/app.py chạy y hệt lúc bình thường.
    """

    def __init__(self, inner):
        self.inner = inner
        self.model_name = getattr(inner, "model_name", "unknown")
        self.reset()

    def reset(self):
        self.calls = []

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        t0 = time.perf_counter()
        out = self.inner.generate(prompt, system_prompt=system_prompt)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        usage = getattr(self.inner, "last_usage", None) or {}
        self.calls.append({
            "latency_ms": round(elapsed_ms, 2),
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
        })
        return out

    # --- tổng hợp ---
    @property
    def total_latency_ms(self):
        return round(sum(c["latency_ms"] for c in self.calls), 2)

    @property
    def total_prompt_tokens(self):
        return sum(c["prompt_tokens"] for c in self.calls)

    @property
    def total_completion_tokens(self):
        return sum(c["completion_tokens"] for c in self.calls)

    def cost_usd(self):
        price = PRICING.get(self.model_name, DEFAULT_PRICE)
        return (self.total_prompt_tokens / 1_000_000 * price["input"]
                + self.total_completion_tokens / 1_000_000 * price["output"])


def percentile(values, pct):
    """P50 / P99 theo kiểu nearest-rank, đủ dùng cho cỡ mẫu nhỏ."""
    if not values:
        return 0.0
    ordered = sorted(values)
    k = max(0, min(len(ordered) - 1, int(round(pct / 100 * len(ordered) + 0.5)) - 1))
    return round(ordered[k], 2)


def grade(tc, result):
    """
    Chấm 1 test case theo 4 tiêu chí 0-2 điểm của CODELAB mục 6.

    Chấm tự động dựa trên tool đã gọi và cách agent kết thúc; phần
    Factual correctness cần người đọc xác nhận nên chỉ chấm phần máy kiểm được.
    """
    required = tc.get("tools_required", [])
    called = result["tools_called"]
    seq = tc.get("expected_tool_sequence")

    # Tool selection
    if not required:
        tool_score = 2 if not called else 1   # câu đơn giản mà vẫn gọi tool là thừa
    elif seq:
        expected_order = [s.split("(")[0] for s in seq]
        tool_score = 2 if called[:len(expected_order)] == expected_order else (1 if set(required) & set(called) else 0)
    else:
        tool_score = 2 if set(required).issubset(set(called)) else (1 if called else 0)

    # Termination
    if result["guardrail_triggered"]:
        term_score = 1   # dừng an toàn nhưng thừa bước
    elif result["steps"] <= max(1, len(required)) + 1:
        term_score = 2
    else:
        term_score = 1

    # Grounding: câu cần tool thì Final Answer phải đến sau khi có Observation
    ground_score = 2 if (not required or called) else 0

    return {
        "tool_selection": tool_score,
        "termination": term_score,
        "grounding": ground_score,
        "passed": tool_score == 2 and term_score == 2 and ground_score == 2,
    }


def main():
    tests = cupid_app.load_test_cases()
    base_provider = get_llm_provider()
    model = getattr(base_provider, "model_name", "unknown")

    print("=" * 60)
    print(f"📊 BENCHMARK — {len(tests)} test case × 2 nhánh (Baseline + ReAct)")
    print(f"   Provider: {base_provider.__class__.__name__} | Model: {model}")
    print("=" * 60)

    rows = []
    for tc in tests:
        print(f"\n▶️  TEST CASE {tc['id']}: {tc['category']}")

        # --- nhánh 1: Chatbot Baseline ---
        m_base = MeteredProvider(base_provider)
        baseline_answer = cupid_app.run_baseline_chatbot(tc["question"], m_base)

        # --- nhánh 2: ReAct Agent ---
        m_react = MeteredProvider(base_provider)
        result = cupid_app.run_react_agent(tc["question"], m_react)

        scores = grade(tc, result)
        rows.append({
            "id": tc["id"],
            "category": tc["category"],
            "question": tc["question"],
            "tools_required": tc.get("tools_required", []),
            "baseline": {
                "answer": baseline_answer,
                "latency_ms": m_base.total_latency_ms,
                "prompt_tokens": m_base.total_prompt_tokens,
                "completion_tokens": m_base.total_completion_tokens,
                "llm_calls": len(m_base.calls),
                "cost_usd": round(m_base.cost_usd(), 6),
            },
            "react": {
                "final_answer": result["final_answer"],
                "steps": result["steps"],
                "tools_called": result["tools_called"],
                "guardrail_triggered": result["guardrail_triggered"],
                "latency_ms": m_react.total_latency_ms,
                "prompt_tokens": m_react.total_prompt_tokens,
                "completion_tokens": m_react.total_completion_tokens,
                "llm_calls": len(m_react.calls),
                "cost_usd": round(m_react.cost_usd(), 6),
            },
            "scores": scores,
        })

    # ----- tổng hợp -----
    react_lat = [r["react"]["latency_ms"] for r in rows]
    base_lat = [r["baseline"]["latency_ms"] for r in rows]
    react_tok = [r["react"]["prompt_tokens"] + r["react"]["completion_tokens"] for r in rows]
    base_tok = [r["baseline"]["prompt_tokens"] + r["baseline"]["completion_tokens"] for r in rows]
    passed = sum(1 for r in rows if r["scores"]["passed"])

    summary = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "model": model,
        "test_cases": len(rows),
        "passed": passed,
        "success_rate_pct": round(passed / len(rows) * 100, 1) if rows else 0.0,
        "react": {
            "latency_p50_ms": percentile(react_lat, 50),
            "latency_p99_ms": percentile(react_lat, 99),
            "latency_mean_ms": round(statistics.mean(react_lat), 2) if react_lat else 0,
            "avg_tokens_per_task": round(statistics.mean(react_tok), 1) if react_tok else 0,
            "total_cost_usd": round(sum(r["react"]["cost_usd"] for r in rows), 6),
        },
        "baseline": {
            "latency_p50_ms": percentile(base_lat, 50),
            "latency_p99_ms": percentile(base_lat, 99),
            "avg_tokens_per_task": round(statistics.mean(base_tok), 1) if base_tok else 0,
            "total_cost_usd": round(sum(r["baseline"]["cost_usd"] for r in rows), 6),
        },
    }
    summary["total_cost_usd"] = round(
        summary["react"]["total_cost_usd"] + summary["baseline"]["total_cost_usd"], 6
    )

    logs_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    out_path = os.path.join(logs_dir, f"benchmark_{datetime.now():%Y%m%d_%H%M%S}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "cases": rows}, f, ensure_ascii=False, indent=2)

    # ----- in bảng Markdown để dán vào report -----
    print("\n" + "=" * 60)
    print("📋 TÓM TẮT (dán vào report)")
    print("=" * 60)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("\n| # | Loại | Tool gọi | Steps | Guardrail | Latency ReAct | Token ReAct | Pass |")
    print("| :-: | :-- | :-- | :-: | :-: | --: | --: | :-: |")
    for r in rows:
        print(f"| {r['id']} | {r['category'][:28]} | {', '.join(r['react']['tools_called']) or '—'} "
              f"| {r['react']['steps']} | {'✅' if r['react']['guardrail_triggered'] else '—'} "
              f"| {r['react']['latency_ms']:.0f}ms | {r['react']['prompt_tokens'] + r['react']['completion_tokens']} "
              f"| {'✅' if r['scores']['passed'] else '❌'} |")
    print(f"\n💾 Chi tiết đầy đủ: {out_path}")


if __name__ == "__main__":
    main()
