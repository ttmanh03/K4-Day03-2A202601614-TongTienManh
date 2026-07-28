# Web UI — Cupid Agent (FastAPI + React)

Repo hiện có **2 bản Web UI song song**, dùng chung `src/` (tools, prompts, providers):

| | Bản này (FastAPI + React) | Bản `server.py` + `web/` |
| :-- | :-- | :-- |
| Backend | `backend/` — FastAPI, SSE streaming | `server.py` — `http.server` thuần |
| Frontend | `frontend/` — React + TypeScript + Tailwind | `web/` — HTML/CSS/JS thuần |
| Cổng backend | **8001** | **8000** |
| Cách chạy | 2 tiến trình (backend + Vite dev) | 1 tiến trình |

Hai bản dùng cổng khác nhau nên **chạy đồng thời được**.

## Chạy bản FastAPI + React

Mở 2 terminal:

```bash
# Terminal 1 — backend (cổng 8001)
python backend/run.py

# Terminal 2 — frontend (cổng 5173)
cd frontend
npm install     # chỉ cần lần đầu
npm run dev
```

Mở http://localhost:5173

## 4 cấp độ AI

Chọn cấp độ ở thanh trên cùng, rồi hỏi cùng một câu để thấy khác biệt:

| Cấp | Tên | Endpoint | Đặc điểm |
| :-: | :-- | :-- | :-- |
| 1 | Rule-Based Bot | `POST /api/chat/level1` | Khớp từ khóa if/else, **không dùng LLM**, trả lời tức thì |
| 2 | LLM Chatbot | `POST /api/chat/baseline` | LLM sinh text mượt nhưng **không gọi được tool** |
| 3 | Reactive Agent | `POST /api/chat/react` (SSE) | `Thought → Action → Observation`, có gọi tool |
| 4 | Autonomous Agent | `POST /api/chat/autonomous` (SSE) | Tự lập kế hoạch → thực thi → **Memory** → tự đánh giá |

Cấp 3 và 4 stream từng bước suy luận qua SSE; bấm chip trong bong bóng chat để
mở panel **"Luồng Suy luận"** xem timeline real-time.

Endpoint phụ: `GET /api/health` (provider đang dùng), `GET /api/test-cases`.

## Cấu hình LLM

Đọc từ `.env` ở thư mục gốc (giống CLI):

```
LLM_PROVIDER=deepseek     # gemini | openai | anthropic | openrouter | deepseek | mock
LLM_MODEL=deepseek-v4-flash
DEEPSEEK_API_KEY=...
```

Dùng `LLM_PROVIDER=mock` để demo offline, không tốn API.

## Chia sẻ qua ngrok

Vite đã bật `host: true` và `allowedHosts: true` nên tunnel được:

```bash
ngrok http 5173
```

## Ghi chú kỹ thuật

`backend/agent_runner.py` chép lại logic `_parse_action` / `_call_tool` / vòng lặp
ReAct từ `src/app.py` (đổi `print()` thành generator yield step-dict để stream).
Nếu `src/app.py` đổi cách parse Action thì cần đồng bộ tay sang đây.
