# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Hùng Mạnh
- **Student ID**: 2A202601256
- **Role**: Role 4 — Core Developer / Integrator
- **Date**: 2026-07-28

---

## I. Technical Contribution (15 Points)

Với vai trò **Role 4 (Integrator)**, phần việc của em không phải viết một tool hay một prompt riêng lẻ, mà là **ghép file của Role 1, 2, 3 thành một ứng dụng chạy được**, rồi mở rộng nó thành hệ thống demo đủ 4 cấp độ AI.

### Modules Implemented

| Module | Nội dung | Mức đóng góp |
| :--- | :--- | :--- |
| `backend/agent_runner.py` | Vòng lặp ReAct có **SSE streaming** cho Web UI, parser Action, guardrails nâng cấp, lớp chống rò rỉ system prompt | **100%** (247/247 dòng) |
| `src/app.py` | Vòng lặp ReAct core chạy CLI — em ghép nối bản đầu và merge với bản align tool của Role 1 | Đồng tác giả (~32 dòng) |
| `backend/levels.py` | Cấp 1 (Rule-Based) và Cấp 4 (Autonomous: Planning → Execution → Self-Evaluation) | 100% |
| `backend/memory.py` | Bộ nhớ 2 tầng: short-term 5 lượt (RAM) + long-term do LLM tự trích xuất (JSON) | 100% |
| `backend/main.py`, `run.py`, `schemas.py` | FastAPI, endpoint cho 4 cấp độ, tách cổng 8001 để chạy song song bản Web UI của Role 1 | 100% |
| `frontend/` | React + TypeScript + Tailwind: `TracePanel`, `TraceStepCard`, `MemoryPanel`, `LevelSelector` | 100% |
| `config/rule_based_kb.json` | Knowledge base 11 luật if/else + fallback cho Cấp 1 | 100% |
| `backend/verify_levels.py`, `verify_guardrails.py` | Script tự kiểm chứng 4 cấp độ và bộ guardrail | 100% |

### Code Highlights

**1. Parser Action chịu được LLM viết sai định dạng** — [`backend/agent_runner.py:22-36`](../../backend/agent_runner.py#L22-L36)

```python
def _parse_action(text: str):
    m = re.search(r'Action:\s*(\w+)\s*\((.*)\)\s*$', text, re.MULTILINE | re.DOTALL)
    if not m:
        return None, None
    ...
    try:
        kwargs = json.loads(raw)
        if isinstance(kwargs, dict):
            return tool_name, kwargs
    except (json.JSONDecodeError, ValueError):
        pass
    # Positional fallback: "val1", "val2"
    parts = [p.strip().strip('"\'') for p in raw.split(',') if p.strip()]
    return tool_name, {"__pos__": parts} if parts else {}
```

Thiết kế 2 tầng: ưu tiên JSON đúng chuẩn, hỏng thì rơi xuống tách tham số theo vị trí. Lý do là LLM **sẽ** sai định dạng, và một parser cứng nhắc sẽ biến mọi lỗi format thành một vòng lặp lãng phí.

**2. Chống lặp Action bằng chữ ký** — [`backend/agent_runner.py:57-73`](../../backend/agent_runner.py#L57-L73)

```python
def _action_signature(tool_name: str, kwargs: dict) -> tuple:
    return (tool_name, json.dumps(kwargs, sort_keys=True, ensure_ascii=False))

# ... trong _call_tool():
if signature in executed_actions:
    return (
        f"LỖI: Action {tool_name}({kwargs}) đã được gọi trước đó, không lặp lại. "
        "Hãy dùng kết quả đã có để đưa ra Final Answer."
    )
```

`sort_keys=True` để `{"a":1,"b":2}` và `{"b":2,"a":1}` được coi là **cùng một Action** — nếu không, agent chỉ cần đảo thứ tự key là lách được phanh chống lặp.

**3. Tách bạch Memory theo cấp độ** — [`backend/memory.py`](../../backend/memory.py)

Đây là quyết định thiết kế em cân nhắc lâu nhất: **chỉ Cấp 4 được dùng memory, Cấp 2 và Cấp 3 thì không.** Lý do ở mục III.2.

### Documentation — Code của em tương tác với ReAct loop thế nào

Em giữ nguyên tắc **không sửa file của người khác**. `src/tools.py` (Role 2) và `src/prompts.py` (Role 3) được import nguyên vẹn; mọi thứ em cần thêm đều nằm ở tầng ghép nối:

```
config/test_cases.json (Role 1) ─┐
src/tools.py           (Role 2) ─┼─→ src/app.py (Role 4) ─→ vòng lặp ReAct
src/prompts.py         (Role 3) ─┘         │
                                           └─→ backend/agent_runner.py ─→ SSE ─→ frontend/
```

*(Repo còn một bản Web UI thứ hai — `server.py` + `web/` — do Role 1 dựng, dùng chung `src/` và chạy ở cổng 8000. Phần em tách cổng 8001 ở `backend/` là để hai bản chạy song song được, không đè nhau.)*

Loop đọc `AVAILABLE_TOOLS` từ Role 2 để vừa **dispatch** vừa **whitelist** — tool nào không có trong dict thì Observation trả về danh sách tool hợp lệ thay vì crash. `MAX_ITERATIONS` và `TIMEOUT_SECONDS` của Role 3 được loop dùng làm ngân sách chạy. Khi cần ghi đè một chỉ dẫn trong prompt của Role 3, em **nối thêm khối mới ở tầng backend** (`NO_SYSTEM_LEAK`) chứ không sửa file gốc — vừa tránh conflict git, vừa giữ đúng phân vai.

---

## II. Debugging Case Study (10 Points)

### Problem Description: Agent rơi Guardrail oan dù đã có sẵn câu trả lời

Khi test Web UI, em thấy nhiều câu hỏi **đơn giản** lại chạy hết cả 4 vòng lặp rồi hiện thông báo safe fallback *"chưa thu thập đủ dữ liệu đáng tin cậy"* — trong khi đọc trace thì thấy **ngay vòng 1 LLM đã trả lời xong rồi**.

### Log Source

Trace panel hiển thị đúng nội dung LLM sinh ra ở mỗi vòng:

```
Step 1: Thought: Câu hỏi này chỉ cần tư vấn chung, không cần tool.
        Final: Một mối quan hệ lành mạnh cần giao tiếp cởi mở, tôn trọng...
        → Observation: Không tìm thấy Action hợp lệ. Hãy đưa ra Final Answer hoặc thử Action khác.
Step 2: (LLM lặp lại nội dung tương tự)
        → Observation: Không tìm thấy Action hợp lệ...
Step 3: ...
Step 4: 🛡️ GUARDRAIL TRIGGERED — safe fallback
```

### Diagnosis

Nguyên nhân gốc nằm ở **một dấu hai chấm**.

`REACT_SYSTEM_PROMPT` quy định nhãn `Final Answer:`, nhưng model (DeepSeek `deepseek-v4-flash`) thường xuyên viết tắt thành **`Final:`**. Điều kiện dừng của loop lúc đó là kiểm tra chuỗi cứng:

```python
if "Final Answer:" in llm_output:   # ← "Final:" không khớp
```

Nên loop **không nhận ra câu trả lời đã sẵn sàng**, tiếp tục quay cho đến hết budget. Đây không phải lỗi model — model trả lời đúng nội dung; cũng không hẳn lỗi prompt — prompt đã nói rõ định dạng. **Lỗi ở chỗ em giả định LLM sẽ tuân thủ định dạng tuyệt đối.** Một hệ thống production không được phép đặt điều kiện dừng lên một chuỗi khớp chính xác do LLM sinh ra.

Tác hại kép: (1) tốn 4× số lần gọi API cho một câu hỏi lẽ ra 1 lượt là xong, (2) người dùng nhận lời xin lỗi thay vì câu trả lời **đã có sẵn** — và trong bài lab thì trace log trông như Agent thất bại, dễ bị đánh giá sai năng lực.

### Solution

Em sửa theo hướng **nới điều kiện nhận diện, không siết thêm prompt** — [`backend/agent_runner.py:48-55`](../../backend/agent_runner.py#L48-L55):

```python
# Prompt yêu cầu "Final Answer:" nhưng LLM hay viết tắt thành "Final:".
# Bắt cả 2 dạng, nếu không agent sẽ chạy phí vòng lặp rồi rơi vào guardrail
# dù đã có sẵn câu trả lời.
FINAL_RE = re.compile(r'Final\s*(?:Answer)?\s*:', re.IGNORECASE)
```

Rồi phòng thủ thêm một lớp cho trường hợp LLM quên hẳn nhãn — [`backend/agent_runner.py:104-112`](../../backend/agent_runner.py#L104-L112):

```python
def _looks_like_answer(text: str) -> bool:
    """Đúng khi LLM viết thẳng câu trả lời mà quên nhãn 'Final Answer:'."""
    stripped = re.sub(r'^\s*Thought:\s*', '', text.strip(), flags=re.IGNORECASE)
    if len(stripped) < 80:
        return False
    return "Action:" not in stripped
```

Heuristic: đoạn text đủ dài (≥80 ký tự) mà **không chứa `Action:`** thì gần như chắc chắn là câu trả lời cho người dùng, không phải một bước suy luận.

Cùng đợt em sửa thêm 3 lỗi cùng họ "hệ thống tin LLM quá mức":

| Lỗi | Sửa |
| :--- | :--- |
| Provider thỉnh thoảng trả `content=None` → UI hiện bong bóng trống | `generate_nonempty()` retry khi nhận chuỗi rỗng — [`agent_runner.py:87`](../../backend/agent_runner.py#L87) |
| Hết budget thì xin lỗi suông, vứt bỏ dữ liệu tool đã tra được | Trả lại phần Observation đã thu thập kèm lời giải thích — [`agent_runner.py:222`](../../backend/agent_runner.py#L222) |
| Action trùng bị báo *sau* khi đã log ra trace → đọc trace hiểu nhầm là gọi tool 2 lần | Chặn dedup **trước** khi ghi trace |

### Verification

Em viết 2 script để lỗi này không tái phát, kết quả **lần chạy gần nhất** (commit `2d626fa`):

- `backend/verify_guardrails.py` — **19 PASS**: 5 đòn tấn công (out-of-scope, dữ liệu bịa, prompt injection, tool không tồn tại, nội dung nhạy cảm) và các case giới hạn vòng lặp.
- `backend/verify_levels.py` — **35 PASS**: mỗi cấp độ đúng vai trò, memory chỉ tồn tại ở Cấp 4, không cấp nào lộ tên tool ra ngoài.

Hai script này gọi LLM thật nên số PASS cần chạy lại để tái xác nhận trước khi demo.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

### 1. Reasoning — khối `Thought` giúp được gì?

Điều em không lường trước: **`Thought` có giá trị với người phát triển nhiều hơn với chất lượng câu trả lời.**

So câu trả lời cuối của TC#4 (INTJ × ENFP + gợi ý hẹn hò), Chatbot baseline viết mượt không kém Agent. Nhưng khi Agent sai, em **đọc được nó sai ở đâu**: Thought 1 chọn tool gì, Observation trả về gì, Thought 2 diễn giải Observation đó ra sao. Với Chatbot, một câu trả lời sai chỉ là một khối văn bản — muốn sửa thì chỉ còn cách sửa prompt rồi cầu may.

`Thought` cũng ép model **cam kết một kế hoạch trước khi hành động**. Ở TC#4, chính việc phải viết ra *"cần phân tích MBTI trước khi gợi ý hẹn hò"* giữ cho nó không nhảy cóc sang `suggest_date_ideas` — thứ tự phụ thuộc được giữ nhờ suy luận được nói thành lời, chứ không phải nhờ code ép buộc.

### 2. Reliability — khi nào Agent **tệ hơn** Chatbot?

Ba trường hợp em quan sát được:

**a) Câu hỏi kiến thức thuần (TC#1, TC#2).** Agent tốn thêm ít nhất một vòng gọi LLM chỉ để kết luận "không cần tool", trong khi Chatbot trả lời thẳng. Chậm hơn, đắt hơn, chất lượng tương đương. Đây là lý do nhóm em làm **Hybrid Flowchart** thay vì đẩy mọi thứ qua Agent.

**b) Khi tool trả kết quả fallback.** Trước khi Role 2 thêm whitelist 12 cung, tool trả "75%" cho cung bịa. Chatbot baseline gặp câu này lại **an toàn hơn** — nó thẳng thắn nói không có dữ liệu. Agent thì có một con số trong tay nên tự tin diễn giải tiếp. **Một Observation sai còn nguy hiểm hơn không có Observation nào**, vì nó khoác cho câu trả lời sai cái vỏ "có căn cứ".

**c) Khi cho Agent bộ nhớ.** Đây là phát hiện làm em phải đổi thiết kế: lúc đầu em định cho cả 4 cấp dùng chung memory. Nhưng test thì thấy **Cấp 3 có memory sẽ ngừng gọi tool** — hỏi lại "MBTI của tôi hợp với ENFP không?" thì nó trả lời thẳng từ lịch sử hội thoại thay vì gọi `analyze_mbti_match`. Nghĩa là memory *bào mòn* đúng cái đặc trưng `Thought → Action → Observation` mà Cấp 3 sinh ra để thể hiện. Kết luận: **chỉ Cấp 4 dùng memory**, ghi rõ trong docstring `backend/memory.py` để người sau không "tối ưu" nhầm.

### 3. Observation — feedback từ môi trường ảnh hưởng bước sau thế nào?

Observation là thứ duy nhất trong vòng lặp mà **LLM không kiểm soát được** — và chính vì thế nó là chỗ neo sự thật.

Điểm em thấy rõ nhất là **Observation lỗi cũng là Observation tốt**. Khi thiết kế `_call_tool()`, em cố ý biến mọi lỗi thành chuỗi mô tả nhét ngược vào context thay vì raise:

```
LỖI: Tool 'book_ring' không tồn tại. Tool hợp lệ: [calculate_zodiac_compatibility, ...]
```

Model đọc được câu này thì **tự sửa ở vòng sau** — thường là chuyển sang từ chối lịch sự vì hiểu ra hành động đó ngoài phạm vi. Nếu em để exception bay ra, loop chết và người dùng nhận stack trace. Nói cách khác, chất lượng tự phục hồi của Agent phụ thuộc trực tiếp vào việc **thông báo lỗi có được viết cho LLM đọc hay không** — đây là góc nhìn em chưa từng nghĩ tới trước bài lab này.

---

## IV. Future Improvements (5 Points)

### Scalability

- **Bất đồng bộ hoá tool call**: TC#4 gọi 2 tool tuần tự vì có phụ thuộc, nhưng các truy vấn kiểu "so sánh 3 cặp cung" thì hoàn toàn chạy song song được bằng `asyncio.gather()`.
- **Chuyển sang LangGraph**: vòng `while` hiện tại đủ tốt cho 3 tool. Khi có phân nhánh điều kiện và nhiều agent con, cần một graph có state rõ ràng thay vì lồng thêm `if` vào loop.
- **Memory backend**: `memory_store.json` hiện là file phẳng + `threading.Lock`. Nhiều session đồng thời thì phải chuyển Redis (short-term) và Postgres (long-term).

### Safety

- **Supervisor LLM**: thêm một model nhỏ, rẻ (ví dụ Haiku) audit Action *trước khi* thực thi — đặc biệt cần khi hệ thống có tool gây tác dụng phụ thật (đặt lịch, thanh toán) chứ không chỉ tool đọc như hiện nay.
- **Chống prompt injection**: `verify_guardrails.py` mới test injection ở tầng câu hỏi người dùng. Rủi ro lớn hơn là **injection qua Observation** — nếu sau này tool đọc dữ liệu từ web, nội dung độc hại sẽ được nhét thẳng vào context. Cần sanitize và đóng khung Observation như dữ liệu không tin cậy.
- **Rate limit + budget trần theo session**, tránh một người dùng đốt hết quota API.

### Performance

- **Telemetry token/cost**: hiện mới đo `execution_time_ms`. Cần đọc `usage` từ response của từng provider, ghi JSONL để tính P50/P99 thật.
- **Vector DB cho tool retrieval**: 3 tool thì nhét hết mô tả vào system prompt là ổn. Vượt ~20 tool thì phải embed mô tả tool và chỉ đưa top-k liên quan vào prompt — vừa tiết kiệm token vừa tăng độ chính xác chọn tool.
- **Cache Observation**: các cặp cung/MBTI được hỏi lại nhiều lần; cache kết quả tool deterministic sẽ cắt được kha khá độ trễ.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
