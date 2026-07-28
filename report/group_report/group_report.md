# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: Cupid Agent — K4 / Lab 03 E402
- **Team Members**:
  | Thành viên | Role | File đảm nhận |
  | :--- | :--- | :--- |
  | Nguyễn Văn Trọng | Role 1 — Product Architect | `config/test_cases.json`, `docs/hybrid_flowchart.mermaid` |
  | Nguyễn Tiến Đạt | Role 2 — Tool Engineer | `src/tools.py` |
  | Nguyễn Văn Thắng | Role 3 — Prompt Engineer | `src/prompts.py` |
  | Nguyễn Hùng Mạnh | Role 4 — Core Developer / Integrator | `src/app.py`, `backend/`, `frontend/` |
  | Tống Tiến Mạnh | Role 5 — Observability | `docs/trace_eval.md` |
- **Deployment Date**: 2026-07-28

---

## 1. Executive Summary

**Bài toán**: *Cupid Agent* — trợ lý phân tích độ tương thích tình cảm (cung hoàng đạo, MBTI) và gợi ý kịch bản hẹn hò theo địa điểm / ngân sách / phong cách.

Nhóm chọn đề tài này vì nó buộc hệ thống phải **tra cứu dữ liệu rồi mới quyết định bước tiếp theo** — đúng đặc trưng cần Agent thay vì Chatbot. Bảng Agentic Fit (`docs/trace_eval.md`) chấm **17/20**, trong đó Multi-step Reasoning và Tool Interaction đều đạt 5/5.

- **Success Rate**: `[CHỜ ĐO — điền sau lần chạy nghiệm thu cuối, xem §3]`
- **Key Outcome**: Trên test case multi-step (TC#4), ReAct Agent gọi đúng **2 tool theo thứ tự phụ thuộc** (`analyze_mbti_match` → `suggest_date_ideas`) và chỉ gợi ý hẹn hò *sau khi* đã có kết quả tương thích. Chatbot baseline trả lời cùng câu hỏi bằng kiến thức chung, nội dung mượt nhưng **không có số liệu kiểm chứng được** và không để lại vết suy luận để audit.

Khác biệt cốt lõi quan sát được không nằm ở "câu trả lời hay hơn", mà ở **khả năng truy vết**: mọi con số Agent đưa ra đều gắn với một Observation cụ thể từ tool.

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation

Vòng lặp cài trong [`src/app.py:94-132`](../../src/app.py#L94-L132), bản phục vụ Web UI ở [`server.py:75-155`](../../server.py#L75-L155).

```mermaid
flowchart TD
    Q[User Query] --> LLM[LLM sinh Thought + Action]
    LLM --> PARSE{Parse được<br/>Action?}
    PARSE -->|Final Answer| DONE([Final Answer])
    PARSE -->|Action hợp lệ| GUARD{Kiểm tra<br/>Guardrail}
    PARSE -->|Không parse được| HINT[Chèn Observation gợi ý<br/>sửa định dạng]
    GUARD -->|Tool lạ| ERR1[LỖI: liệt kê tool hợp lệ]
    GUARD -->|Action trùng| ERR2[LỖI: đã gọi rồi, đổi cách khác]
    GUARD -->|Hợp lệ| EXEC[Thực thi tool]
    EXEC --> OBS[Observation]
    ERR1 --> OBS
    ERR2 --> OBS
    HINT --> OBS
    OBS --> BUDGET{step < MAX_ITERATIONS?}
    BUDGET -->|Còn budget| LLM
    BUDGET -->|Hết| FALLBACK([Safe Fallback lịch sự])
```

**4 nguyên tắc bất biến nhóm áp dụng khi code loop:**

1. **Mỗi lượt đúng 1 Action** — prompt ép LLM dừng lại sau khi ra Action để hệ thống thực thi.
2. **Observation do hệ thống chèn, không phải LLM tự sinh** — LLM không được phép bịa kết quả tool.
3. **Không lượt nào được thoát mà không có kết luận** — hết budget vẫn phải trả Safe Fallback, không im lặng.
4. **Mọi lỗi đều biến thành Observation dạng text**, không bao giờ raise ra ngoài loop ([`src/app.py:71-91`](../../src/app.py#L71-L91)).

**Ngoài phạm vi Lab**, nhóm còn dựng đủ **4 cấp độ AI hội thoại** để so sánh trực quan trên cùng một Web UI (`backend/levels.py`, `backend/agent_runner.py`): Cấp 1 Rule-Based (`config/rule_based_kb.json`, không gọi LLM) → Cấp 2 LLM Chatbot → Cấp 3 ReAct Agent → Cấp 4 Autonomous Agent (Planning + Memory + Self-Evaluation).

### 2.2 Tool Definitions (Inventory)

| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `calculate_zodiac_compatibility` | `json` — `{"zodiac_1": str, "zodiac_2": str}` | Tra cứu điểm tương thích giữa 2 cung hoàng đạo. **Có whitelist 12 cung chuẩn**, tên lạ bị chặn ngay tại tool. |
| `analyze_mbti_match` | `json` — `{"mbti_1": str, "mbti_2": str}` | Phân tích độ ăn ý / bù trừ giữa 2 nhóm tính cách MBTI. |
| `suggest_date_ideas` | `json` — `{"location": str, "budget": str, "vibe": str}` | Sinh kịch bản hẹn hò 3 chặng theo địa điểm, ngân sách, phong cách. |

Cả 3 tool đều tuân thủ chung một contract ([`src/tools.py`](../../src/tools.py)): validate tham số rỗng/sai kiểu trước → bọc `try/except` toàn thân → **luôn trả về `str`**, không bao giờ raise. Registry tập trung tại `AVAILABLE_TOOLS` ([`src/tools.py:126-130`](../../src/tools.py#L126-L130)) để loop tra cứu và whitelist.

### 2.3 LLM Providers Used

Nhóm viết một lớp adapter đa nhà cung cấp ([`src/providers.py:287-302`](../../src/providers.py#L287-L302)), chọn qua biến môi trường `LLM_PROVIDER` nên đổi provider không phải sửa code.

- **Primary**: DeepSeek `deepseek-v4-flash` (cấu hình đang chạy)
- **Secondary (Backup)**: Gemini `gemini-2.5-flash`, OpenAI `gpt-4o-mini`, Anthropic `claude-3-haiku`, OpenRouter
- **Offline**: `MockProvider` — chạy demo được khi hết quota hoặc mất mạng, dùng làm phương án dự phòng lúc trình bày

> Lý do chọn DeepSeek làm primary: trong quá trình làm Mốc 2, key Gemini của nhóm bị quota 0 nên đã bổ sung DeepSeek làm fallback (commit `edf3ee4`).

---

## 3. Telemetry & Performance Dashboard

### 3.1 Hiện trạng đo đạc

| Chỉ số | Trạng thái | Nguồn |
| :--- | :--- | :--- |
| Latency mỗi request | ✅ Đã instrument | `execution_time_ms` tại [`server.py:143`](../../server.py#L143) |
| Latency Cấp 1 (rule-based) | ✅ Đã có assertion | [`backend/verify_levels.py:88-93`](../../backend/verify_levels.py#L88-L93) — khẳng định `< 0.5s`, đủ chứng minh **không** có API call tới LLM |
| Số bước ReAct / lần chạm guardrail | ✅ Đã ghi | `total_steps`, `guardrail_triggered` trong payload trả về của `execute_full_flow()` |
| Token per task | ❌ Chưa instrument | Provider adapter chưa đọc `usage` từ response |
| Cost | ❌ Chưa instrument | Phụ thuộc token count ở trên |

### 3.2 Số liệu lần chạy nghiệm thu

> [!IMPORTANT]
> Các ô dưới đây **cố ý để trống** cho tới khi chạy `python src/app.py` trên đủ 5 test case ở lần nghiệm thu cuối. Nhóm không điền số ước lượng để tránh báo cáo sai lệch.

- **Average Latency (P50)**: `[CHỜ ĐO]` ms
- **Max Latency (P99)**: `[CHỜ ĐO]` ms
- **Average Tokens per Task**: `[CHỜ ĐO]` — cần bổ sung đọc `usage` trong `src/providers.py` trước
- **Total Cost of Test Suite**: `[CHỜ ĐO]`

### 3.3 Việc cần làm để hoàn thiện dashboard

1. Đọc `response.usage.prompt_tokens / completion_tokens` trong từng provider class, gắn vào giá trị trả về.
2. Cộng dồn theo task rồi nhân đơn giá `deepseek-v4-flash` để ra cost.
3. Ghi mỗi lần chạy xuống `logs/YYYY-MM-DD.jsonl` để tính được P50/P99 thay vì chỉ có 1 mẫu.

---

## 4. Root Cause Analysis (RCA) - Failure Traces

### Case Study 1: Tool nhận cung hoàng đạo bịa mà vẫn trả điểm số

- **Input**: TC#5 — *"Phân tích độ tương thích cung hoàng đạo giữa 'Thiên Mã Tọa' và 'Ngân Hà Tinh'..."*
- **Observation (bản lỗi)**: `calculate_zodiac_compatibility` rơi thẳng xuống nhánh mặc định và trả `75% - Độ tương thích mức trung bình khá`.
- **Root Cause**: Tool chỉ có **matrix các cặp đã biết** và một `return` mặc định ở cuối, **không có bước validate tên cung đầu vào**. Với LLM thì "75%" là một Observation hợp lệ, nên Agent tin và diễn giải tiếp — lỗi nằm ở *tool contract*, không phải ở prompt.
- **Tác động**: Agent tạo cảm giác hệ thống có dữ liệu về một cung hoàng đạo không tồn tại → hallucination có "bằng chứng giả".
- **Fix (Role 2)**: Bổ sung whitelist `VALID_ZODIACS` 12 cung, chặn ngay đầu hàm ([`src/tools.py:21-35`](../../src/tools.py#L21-L35)). Sau fix, cùng input trả về:
  ```
  Cảnh báo: Tên cung hoàng đạo không hợp lệ hoặc không thuộc 12 cung tiêu chuẩn:
  Thiên Mã Tọa, Ngân Hà Tinh. Vui lòng cung cấp cung hợp lệ (ví dụ: Bảo Bình, Sư Tử...).
  ```
- **Bài học**: Guardrail đặt ở prompt là *khuyến nghị*, đặt ở tool là *bắt buộc*. Với dữ liệu có tập giá trị đóng (12 cung, 16 MBTI), whitelist tại tool rẻ và chắc hơn mọi câu dặn dò trong system prompt.

### Case Study 2: LLM trả lời không đúng định dạng, loop không parse được Action

- **Observation**: Ở một số lượt, model trả về văn xuôi giải thích thay vì dòng `Action: tool_name({...})`, khiến regex parser không khớp.
- **Root Cause**: System prompt v1 mô tả định dạng nhưng **thiếu ràng buộc "mỗi lượt chỉ một Action rồi dừng"**, nên model có xu hướng viết luôn cả phần diễn giải.
- **Fix (Role 3 + Role 4)**: Hai lớp phòng thủ —
  - *Prompt*: siết định dạng bắt buộc và ví dụ Action cụ thể (xem §5, Experiment 1).
  - *Parser*: `_parse_action()` thử `json.loads` trước, thất bại thì fallback sang tách tham số positional ([`src/app.py:53-68`](../../src/app.py#L53-L68)); nếu vẫn không parse được thì **không crash mà chèn Observation hướng dẫn sửa** ([`src/app.py:126-129`](../../src/app.py#L126-L129)), cho model một cơ hội tự phục hồi trong budget còn lại.
- **Bài học**: Parser phải giả định LLM sẽ sai định dạng, và mọi lỗi parse phải trở thành *feedback* cho vòng sau chứ không phải điểm dừng.

> [!NOTE]
> Trace log đầy đủ dạng `Thought → Action → Observation` cho TC#4 và TC#5 xem tại [`docs/trace_eval.md`](../../docs/trace_eval.md) §3.

---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt v1 vs Prompt v2

So sánh hai revision thật của `src/prompts.py`: `e6b8c61` (v1) → `4ca8d81` (v2).

| # | Diff | Vấn đề nhắm tới |
| :-: | :--- | :--- |
| 1 | Thêm ràng buộc thứ tự: *"Với yêu cầu INTJ/ENFP kèm gợi ý hẹn hò, bắt buộc gọi `analyze_mbti_match` trước; chỉ gọi `suggest_date_ideas` sau khi đã nhận Observation"* | Agent có lúc gợi ý hẹn hò trước khi biết hai người có hợp không → sai logic phụ thuộc của TC#4 |
| 2 | Thêm: *"Không thực hiện các yêu cầu ngoài registry (đặt nhẫn, đặt lịch, gửi tin nhắn); từ chối ngắn gọn vì ngoài phạm vi"* | Bẫy out-of-scope ở TC#5 |
| 3 | Siết baseline: *"Tuyệt đối không sinh Thought, Action hoặc Observation; không giả lập kết quả của bất kỳ công cụ nào"* | Chatbot baseline giả vờ đã gọi tool → làm hỏng phép so sánh với Agent |

- **Result**: TC#4 sau v2 chạy đúng thứ tự 2 tool; TC#5 Agent từ chối hành động "đặt nhẫn đính hôn" thay vì tìm cách đáp ứng. Mức giảm lỗi định lượng: `[CHỜ ĐO — cần chạy lại bộ 5 case trên cả 2 revision]`.

### Experiment 2 (Bonus): Chatbot vs Agent

| Case | Chatbot Result | Agent Result | Winner |
| :--- | :--- | :--- | :--- |
| TC#1 — Yếu tố của mối quan hệ lành mạnh (đơn giản) | Đúng, tự nhiên, không cần tool | Đúng, nhưng tốn thêm 1 vòng suy luận | **Draw** (Chatbot rẻ hơn) |
| TC#3 — Bảo Bình × Thiên Bình (single-step) | Chung chung, không có số liệu | `[CHỜ TRACE]` | `[CHỜ TRACE]` |
| TC#4 — INTJ × ENFP + gợi ý hẹn hò (multi-step) | Trả lời mượt nhưng **không có căn cứ kiểm chứng** | Gọi đúng 2 tool theo thứ tự, kết luận gắn với Observation | **Agent** |
| TC#5 — Cung bịa + đòi đặt nhẫn (edge case) | Từ chối an toàn, nhưng không xác minh được gì | Gọi tool → tool chặn input sai → từ chối đúng cả 2 vế của bẫy | **Agent** |

**Kết luận**: Agent **không** thắng ở mọi mặt trận. Với câu hỏi kiến thức thuần (TC#1, TC#2), Chatbot cho kết quả tương đương mà nhanh và rẻ hơn hẳn — đây chính là lý do nhóm thiết kế **Hybrid Flowchart** ([`docs/hybrid_flowchart.mermaid`](../../docs/hybrid_flowchart.mermaid)) để phân luồng thay vì đẩy mọi câu hỏi qua Agent.

---

## 6. Production Readiness Review

### Security

- **Quản lý secret**: `.env` nằm trong `.gitignore` và đã xác minh bằng `git ls-files` — repo **chỉ** track `.env.example`, không rò rỉ API key nào.
- **Chống rò rỉ system prompt**: khối `NO_SYSTEM_LEAK` ([`backend/agent_runner.py:119-134`](../../backend/agent_runner.py#L119-L134)) được nối vào system prompt của **cả 4 cấp độ**, cấm model nhắc tên hàm nội bộ, từ "Observation", "system prompt", "agent" trong câu trả lời cho người dùng cuối. Người dùng nhận kết quả như từ một tư vấn viên, không thấy cơ chế bên trong.
- **Input sanitization**: validate tại tool (whitelist 12 cung, kiểm tra kiểu và rỗng) thay vì tin vào tham số LLM sinh ra.
- **Còn thiếu**: chưa có rate limit và chưa chống prompt injection từ phía người dùng (ví dụ *"bỏ qua mọi chỉ dẫn trước đó"*).

### Guardrails

| Cơ chế | Cài đặt | Vị trí |
| :--- | :--- | :--- |
| Giới hạn vòng lặp | `MAX_ITERATIONS = 4` | `src/prompts.py:80` |
| Timeout | `TIMEOUT_SECONDS = 10` | `src/prompts.py:81` |
| Chặn tool không tồn tại | Whitelist `AVAILABLE_TOOLS`, trả kèm danh sách tool hợp lệ | `src/app.py:75-77` |
| Chống lặp Action | Dedup theo chữ ký `(tool_name, kwargs)` | `src/app.py:79-80` |
| Safe fallback | Trả lời lịch sự khi hết budget, không im lặng | `src/app.py:131-132` |
| Từ chối out-of-scope | Quy định trong `REACT_SYSTEM_PROMPT` | `src/prompts.py:72-73` |

Có script tự kiểm chứng guardrail: `backend/verify_guardrails.py` và `backend/verify_levels.py`.

### Scaling

- **Điều phối**: chuyển sang **LangGraph** khi số nhánh điều kiện tăng — vòng `while` hiện tại đủ cho 3 tool nhưng sẽ khó bảo trì khi có phân nhánh song song.
- **Hiệu năng**: gọi tool bất đồng bộ (`asyncio`) cho các bước độc lập; hiện Web UI đã dùng **SSE streaming** nên người dùng thấy từng bước Thought/Action ngay thay vì chờ trọn vòng lặp.
- **Nhiều tool**: khi vượt ~20 tool, nhét toàn bộ mô tả vào system prompt sẽ tốn token và giảm độ chính xác chọn tool → dùng **Vector DB retrieve top-k tool** liên quan rồi mới đưa vào prompt.
- **Bộ nhớ**: `backend/memory_store.json` hiện là file phẳng, đủ cho demo nhưng cần chuyển sang Redis/Postgres khi có nhiều session đồng thời (hiện đã có `threading.Lock` chống race condition — `backend/memory.py:22`).
- **Observability**: bổ sung ghi log JSONL + token/cost như §3.3 để có dashboard thật thay vì đo thủ công.

---

> [!NOTE]
> Submit this report by renaming it to `GROUP_REPORT_[TEAM_NAME].md` and placing it in this folder.
