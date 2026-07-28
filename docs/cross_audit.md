# 📋 BIÊN BẢN CROSS-AUDIT (MỐC 4)

*Artifact bắt buộc của Tiêu chí 4 — Inter-group Attack & Defense (20%), xem `README.md`.*

- **Ngày**: 2026-07-28
- **Người thuyết trình / phản biện**: Nguyễn Hùng Mạnh (Role 4 — Core Developer / Integrator)
- **Người thao tác demo**: Tống Tiến Mạnh (Role 5 — Observability)
- **Ghi biên bản**: Tống Tiến Mạnh

---

## 1. Nội dung buổi audit

Nhóm trình chiếu App qua Web UI (`backend/` + `frontend/`), demo đủ **4 cấp độ AI** (Rule-Based → LLM Chatbot → Reactive Agent → Autonomous Agent) trên cùng bộ câu hỏi thuộc chủ đề Cupid Agent, để giảng viên/nhóm bạn đối chiếu trực tiếp sự khác biệt giữa các cấp.

## 2. Nhận xét từ buổi phản biện

**Đánh giá chung**: Nhóm hoàn thành đủ cả 4 phần được yêu cầu, hệ thống chạy ổn định trong lúc demo, không phát sinh lỗi hay crash.

**Hai điểm cần cải thiện được ghi nhận:**

### 2.1 Ranh giới Cấp độ 2 và Cấp độ 3 chưa rõ ràng

- **Nhận xét**: Khi xem câu trả lời cuối cùng, người quan sát khó phân biệt đâu là Chatbot (Cấp 2, không tool) và đâu là ReAct Agent (Cấp 3, có tool) — hai câu trả lời trông tương tự nhau nếu không mở kèm Trace Panel.
- **Nguyên nhân (đối chiếu code)**: Đây là hệ quả trực tiếp của cơ chế chống rò rỉ hệ thống (`NO_SYSTEM_LEAK` trong `backend/agent_runner.py`) — quy tắc bắt buộc *"không nhắc tên tool/hàm nội bộ, không dùng cụm từ lộ cơ chế (Observation, tool trả về...)"* nhằm mục đích cho người dùng cuối trải nghiệm tự nhiên. Tác dụng phụ: nếu chỉ nhìn câu trả lời văn bản, khán giả không thấy bằng chứng rằng Cấp 3 vừa gọi tool thật.
- **Điểm nhóm cần làm rõ hơn khi trình bày lần sau**: chủ động mở **Trace Panel** (`frontend/src/components/TracePanel.tsx`, `TraceStepCard.tsx`) song song lúc demo Cấp 3, để khán giả thấy trực tiếp chuỗi `Thought → Action → Observation` thay vì chỉ đọc câu trả lời cuối.

### 2.2 Tool còn đơn giản ("hơi bot"), cần dữ liệu thật hơn

- **Nhận xét**: Cả 3 tool (`calculate_zodiac_compatibility`, `analyze_mbti_match`, `suggest_date_ideas`) đang dựa trên bảng tra cứu (lookup table) viết cứng trong code, không lấy dữ liệu từ nguồn ngoài — cảm giác giống mô phỏng hơn là công cụ thật.
- **Đối chiếu code — đúng như nhận xét**:
  - `calculate_zodiac_compatibility`: chỉ có 3 cặp cung được định nghĩa cứng (`src/tools.py:37-41`), mọi cặp còn lại đều rơi vào một câu trả lời mặc định "75%".
  - `analyze_mbti_match`: tương tự, 3 cặp MBTI cứng (`src/tools.py:71-75`), phần còn lại trả "70–80%" chung chung.
  - `suggest_date_ideas`: kịch bản hẹn hò chỉ viết sẵn cho Hà Nội và TP.HCM (`src/tools.py:107-115`), địa điểm khác dùng template rất chung.
- **Hướng khắc phục đề xuất** (chưa làm, ghi nhận cho lần sau):
  1. Mở rộng bảng tra cứu cung hoàng đạo/MBTI đầy đủ 12×12 và 16×16 thay vì 3 cặp mẫu.
  2. Cân nhắc tool gọi API thật (ví dụ dữ liệu địa điểm/thời tiết) cho `suggest_date_ideas` để không phụ thuộc hoàn toàn vào text viết sẵn.
  3. Nếu vẫn giữ dữ liệu tĩnh (phù hợp vì đây là domain chủ quan, không có "đáp án đúng" khách quan), nên nói rõ trong lúc demo rằng đây là **bảng tri thức được thiết kế có chủ đích**, không phải hạn chế kỹ thuật — tránh bị hiểu nhầm là tool giả.

## 3. Phòng thủ Guardrail — không bị khai thác thêm lỗi mới

Buổi audit không phát hiện lỗi crash hay Agent bị lừa thực hiện hành động ngoài phạm vi. Các cơ chế đã kiểm chứng trước đó (`backend/verify_guardrails.py` — 19 PASS) tiếp tục đứng vững trong lúc demo trực tiếp:

- Không tool nào bị gọi sai tên.
- Không xảy ra lặp vô hạn (`MAX_ITERATIONS = 4` chưa lần nào bị chạm trong buổi demo).
- Agent từ chối đúng các yêu cầu ngoài registry khi được hỏi thử.

## 4. Kết luận

| Hạng mục | Kết quả |
| :--- | :--- |
| Phản biện / trả lời câu hỏi | Đạt — trả lời rõ ràng cơ chế 4 cấp độ, thừa nhận đúng 2 điểm hạn chế thay vì né tránh |
| Agent chống đỡ / fallback | Đạt — không lỗi, không bị khai thác guardrail trong buổi demo |
| Góp ý cải thiện | 2 điểm: (1) làm rõ ranh giới Cấp 2/3 bằng Trace Panel khi trình bày, (2) tool cần depth dữ liệu lớn hơn hoặc nói rõ đây là tri thức chủ đích |

**Việc cần làm sau audit** (không bắt buộc trong phạm vi Lab, ghi nhận để cải tiến nếu còn thời gian): mở rộng dữ liệu tra cứu ở `src/tools.py` theo mục 2.2, và chuẩn bị thao tác mở Trace Panel sẵn trước khi demo Cấp 3 ở lần trình bày kế tiếp.
