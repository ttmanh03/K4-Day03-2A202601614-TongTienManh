# 🛠️ Tool Contract — Cupid Agent

> **Tác giả**: Role 1 — Product Architect  
> **Mục đích**: Đặc tả chính thức cho Role 2 (Tool Engineer) implement `src/tools.py`.  
> Đây là "hợp đồng kỹ thuật" — Role 4 và Role 3 đọc file này để biết tên hàm chính xác, input/output format.

---

## 📦 Data Source

Toàn bộ data mock được lưu tại: `config/cupid_data.json`  
Role 2 đọc file JSON này thay vì hardcode data trong `tools.py`.

---

## 🔧 Danh sách Tool cần implement

### Tool 1: `get_user_profile(user_id: str) -> str`

| Field | Chi tiết |
|:------|:---------|
| **Purpose** | Tra cứu thông tin hồ sơ cá nhân của một người dùng theo ID. Dùng khi Agent cần biết thông tin cụ thể về một người. |
| **Input** | `user_id: str` — ID người dùng, định dạng `"U001"` đến `"U010"` |
| **Output (Success)** | Chuỗi JSON string chứa: name, age, gender, location, occupation, interests, personality_type, relationship_goal, dealbreakers, bio |
| **Output (Error)** | `"LỖI: Không tìm thấy người dùng với ID '{user_id}'. ID hợp lệ trong hệ thống: U001–U010."` |
| **Side effect** | Read-only. Không thay đổi trạng thái hệ thống. |
| **Safety** | Bắt `KeyError`, `FileNotFoundError` — KHÔNG để crash. |

**Ví dụ:**
```python
get_user_profile("U007")
# → '{"id": "U007", "name": "Vũ Thị Lan Hương", "age": 29, ...}'

get_user_profile("U999")
# → "LỖI: Không tìm thấy người dùng với ID 'U999'. ID hợp lệ trong hệ thống: U001–U010."
```

---

### Tool 2: `find_matches(user_id: str) -> str`

| Field | Chi tiết |
|:------|:---------|
| **Purpose** | Tìm danh sách người dùng phù hợp nhất với một người dùng cho trước, xếp hạng theo điểm tương thích. Dùng trước `analyze_compatibility` để biết AI nên so sánh với ai. |
| **Input** | `user_id: str` — ID của người cần tìm kết quả |
| **Output (Success)** | Chuỗi JSON string chứa danh sách xếp hạng: rank, user_id, compatibility_score, match_reason |
| **Output (Error)** | `"LỖI: Không tìm thấy kết quả ghép đôi cho ID '{user_id}'. Người dùng không tồn tại hoặc chưa có dữ liệu."` |
| **Side effect** | Read-only. |
| **Safety** | Bắt mọi exception — KHÔNG để crash. |

**Ví dụ:**
```python
find_matches("U007")
# → '[{"rank": 1, "user_id": "U004", "compatibility_score": 88, ...}, ...]'

find_matches("U999")
# → "LỖI: Không tìm thấy kết quả ghép đôi cho ID 'U999'. ..."
```

---

### Tool 3: `analyze_compatibility(user_a_id: str, user_b_id: str) -> str`

| Field | Chi tiết |
|:------|:---------|
| **Purpose** | Phân tích chi tiết mức độ tương thích giữa hai người dùng cụ thể. Gọi SAU `find_matches` hoặc khi biết rõ cả hai ID. |
| **Input** | `user_a_id: str`, `user_b_id: str` — ID của hai người cần so sánh |
| **Output (Success)** | Chuỗi JSON string chứa: score (0–100), strengths (list), concerns (list), recommendation |
| **Output (Error — 1 hoặc 2 user không tồn tại)** | `"LỖI: Không thể phân tích — Không tìm thấy người dùng: {danh sách ID lỗi}. Kiểm tra lại ID đầu vào."` |
| **Output (Error — cặp chưa có dữ liệu)** | `"LỖI: Chưa có dữ liệu tương thích cho cặp {user_a_id}-{user_b_id}. Vui lòng thử cặp đã được hệ thống tính toán."` |
| **Side effect** | Read-only. |
| **Safety** | Validate cả hai user ID trước khi tra bảng. Bắt mọi exception. |

**Ví dụ:**
```python
analyze_compatibility("U007", "U004")
# → '{"score": 88, "strengths": [...], "concerns": [...], "recommendation": "..."}'

analyze_compatibility("U999", "U000")
# → "LỖI: Không thể phân tích — Không tìm thấy người dùng: U999, U000. Kiểm tra lại ID đầu vào."

analyze_compatibility("U007", "U006")
# → "LỖI: Chưa có dữ liệu tương thích cho cặp U007-U006. ..."
```

---

## ⚠️ Quy tắc bắt buộc cho Role 2

1. **KHÔNG hardcode data trong `tools.py`** — đọc từ `config/cupid_data.json`.
2. **Mọi hàm đều phải trả về `str`** — không trả về `dict`, `None`, hoặc raise exception ra ngoài.
3. **Format lỗi thống nhất**: Bắt đầu bằng `"LỖI:"` để Role 3 (Prompt Engineer) có thể nhận dạng và xử lý trong ReAct loop.
4. **Đăng ký vào `AVAILABLE_TOOLS`**:
```python
AVAILABLE_TOOLS = {
    "get_user_profile": get_user_profile,
    "find_matches": find_matches,
    "analyze_compatibility": analyze_compatibility,
}
```

---

## 🗺️ Mapping Test Case → Tool

| Test Case | Tools được gọi | Thứ tự bắt buộc |
|:----------|:--------------|:----------------|
| TC-1 (LLM only) | Không có | — |
| TC-2 (LLM only) | Không có | — |
| TC-3 (Single-step) | `get_user_profile("U007")` | 1 bước |
| TC-4 (Multi-step) | `find_matches("U007")` → `analyze_compatibility("U007", "U004")` | Bước 1 TRƯỚC bước 2 |
| TC-5 (Edge Case) | `analyze_compatibility("U999", "U000")` | Tool báo lỗi → Agent ngắt |
