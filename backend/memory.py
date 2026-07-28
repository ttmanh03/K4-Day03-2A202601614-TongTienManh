"""
Bộ nhớ hội thoại cho Cupid Agent — 2 tầng:

1. SHORT-TERM (working memory): 5 lượt hội thoại gần nhất, giữ trong RAM theo
   session_id, nạp vào prompt để bot hiểu ngữ cảnh câu hỏi nối tiếp
   ("còn người ấy thì sao?", "vậy đi đâu?"...).

2. LONG-TERM (persistent memory): các fact quan trọng về người dùng (MBTI, cung
   hoàng đạo, thành phố, ngân sách, sở thích...) do LLM tự trích xuất sau mỗi
   lượt, ghi xuống backend/memory_store.json nên còn nguyên sau khi restart.
"""

import json
import os
import re
import threading

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory_store.json")

SHORT_TERM_TURNS = 5  # số lượt hội thoại gần nhất dùng làm context

_lock = threading.Lock()
_short_term: dict[str, list[dict]] = {}  # session_id -> [{"user":..., "assistant":...}]


# ---------------------------------------------------------------------------
# SHORT-TERM MEMORY
# ---------------------------------------------------------------------------

def add_turn(session_id: str, user_msg: str, assistant_msg: str) -> None:
    """Lưu 1 lượt hội thoại, chỉ giữ lại SHORT_TERM_TURNS lượt gần nhất."""
    with _lock:
        turns = _short_term.setdefault(session_id, [])
        turns.append({"user": user_msg, "assistant": assistant_msg})
        del turns[:-SHORT_TERM_TURNS]


def get_recent_turns(session_id: str) -> list[dict]:
    with _lock:
        return list(_short_term.get(session_id, []))


def format_short_term(session_id: str) -> str:
    """Định dạng 5 lượt gần nhất thành text để chèn vào prompt."""
    turns = get_recent_turns(session_id)
    if not turns:
        return ""
    lines = [f"Người dùng: {t['user']}\nCupid: {t['assistant']}" for t in turns]
    return "LỊCH SỬ HỘI THOẠI GẦN ĐÂY:\n" + "\n\n".join(lines)


# ---------------------------------------------------------------------------
# LONG-TERM MEMORY
# ---------------------------------------------------------------------------

def _load_store() -> dict:
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_store(store: dict) -> None:
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(store, f, ensure_ascii=False, indent=2)
    except OSError:
        pass  # không cho lỗi ghi file làm chết request


def get_long_term(session_id: str) -> dict:
    with _lock:
        return _load_store().get(session_id, {})


def format_long_term(session_id: str) -> str:
    """Định dạng fact đã nhớ thành text để chèn vào prompt."""
    facts = get_long_term(session_id)
    if not facts:
        return ""
    lines = [f"- {k}: {v}" for k, v in facts.items()]
    return "THÔNG TIN ĐÃ GHI NHỚ VỀ NGƯỜI DÙNG:\n" + "\n".join(lines)


def clear_memory(session_id: str) -> None:
    with _lock:
        _short_term.pop(session_id, None)
        store = _load_store()
        store.pop(session_id, None)
        _save_store(store)


EXTRACTOR_PROMPT = """Bạn là bộ trích xuất bộ nhớ dài hạn cho trợ lý hẹn hò Cupid.

Đọc đoạn hội thoại và rút ra CHỈ những thông tin bền vững, đáng nhớ lâu dài về
NGƯỜI DÙNG hoặc người mà họ quan tâm. Ví dụ: MBTI, cung hoàng đạo, thành phố
đang sống, ngân sách hẹn hò, sở thích, tên người ấy, tình trạng mối quan hệ.

TUYỆT ĐỐI KHÔNG lưu: câu hỏi nhất thời, kết quả tool, lời chào, nội dung không
nói về người dùng.

Trả về DUY NHẤT một JSON object phẳng dạng {"khóa": "giá trị"}, khóa tiếng Việt
ngắn gọn. Nếu không có gì đáng nhớ, trả về {}.

Ví dụ: {"MBTI của người dùng": "INTJ", "Thành phố": "Hà Nội"}"""


def extract_and_store(session_id: str, user_msg: str, assistant_msg: str, provider) -> dict:
    """
    Dùng LLM trích xuất fact quan trọng rồi merge vào long-term memory.
    Trả về dict các fact MỚI được thêm (rỗng nếu không có gì).
    Mọi lỗi đều nuốt để không làm hỏng luồng chat chính.
    """
    convo = f"Người dùng: {user_msg}\nCupid: {assistant_msg}"
    try:
        raw = provider.generate(convo, system_prompt=EXTRACTOR_PROMPT)
    except Exception:
        return {}

    match = re.search(r"\{.*\}", raw or "", re.DOTALL)
    if not match:
        return {}
    try:
        facts = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}
    if not isinstance(facts, dict) or not facts:
        return {}

    facts = {str(k): str(v) for k, v in facts.items() if k and v}

    with _lock:
        store = _load_store()
        existing = store.setdefault(session_id, {})
        new_facts = {k: v for k, v in facts.items() if existing.get(k) != v}
        existing.update(facts)
        _save_store(store)

    return new_facts


def build_context(session_id: str) -> str:
    """Ghép long-term + short-term thành khối context chèn vào system prompt."""
    parts = [p for p in (format_long_term(session_id), format_short_term(session_id)) if p]
    return "\n\n".join(parts)
