# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Văn Trọng
- **Student ID**: 2A202601102
- **Role**: Role 1 - Product Architect
- **Date**: 28/07/2026

---

## I. Technical Contribution (15 Points)

Là **Product Architect (Role 1)** của dự án **Cupid Agent**, đóng góp kỹ thuật chính của tôi tập trung vào việc định hướng bài toán sản phẩm, thiết kế kiến trúc bộ dữ liệu thử nghiệm và xây dựng kịch bản kiểm thử toàn diện tại tệp `config/test_cases.json`.

- **Modules Implemented**: `config/test_cases.json` (Hệ thống 5 Test Cases chuẩn hóa bao gồm các mức độ: Đơn giản, Single-step, Multi-step và Edge Case bẫy kép).
- **Code Highlights**:
  ```json
  {
    "id": 4,
    "category": "🟡 Multi-step (Cần 2 Tools — Phân tích MBTI rồi gợi ý hẹn hò)",
    "question": "Tôi là INTJ và người ấy là ENFP. Chúng tôi có hợp nhau không? Nếu có, hãy gợi ý một buổi hẹn hò lãng mạn ở Hà Nội với ngân sách trung bình.",
    "expected_behavior": "Agent thực hiện đúng 2 bước theo thứ tự: (1) Gọi analyze_mbti_match để phân tích INTJ-ENFP. (2) Dựa vào kết quả Observation bước 1, gọi tiếp suggest_date_ideas với location='Hà Nội', budget='trung bình', vibe='lãng mạn'.",
    "tools_required": ["analyze_mbti_match", "suggest_date_ideas"],
    "expected_tool_sequence": [
      "analyze_mbti_match({\"mbti_1\": \"INTJ\", \"mbti_2\": \"ENFP\"})",
      "suggest_date_ideas({\"location\": \"Hà Nội\", \"budget\": \"trung bình\", \"vibe\": \"lãng mạn\"})"
    ]
  }
  ```
- **Documentation**: 
  - Đã định nghĩa rõ ranh giới giữa các bài toán chỉ cần Chatbot thông thường (TC#1, TC#2) và các bài toán bắt buộc sử dụng ReAct Agent (TC#3, TC#4, TC#5).
  - Bộ Test Cases quy định chính xác chuỗi gọi công cụ mong đợi (`expected_tool_sequence`), giúp các thành viên khác (Role 4 - Integrator & Role 5 - Observability) có cơ sở đối chiếu, chấm điểm Trace Log và đánh giá chính xác khả năng suy luận của Agent.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**: 
  Trong quá trình kiểm thử Test Case #5 (Edge Case bẫy kép: *"Phân tích độ tương thích cung hoàng đạo giữa 'Thiên Mã Tọa' và 'Ngân Hà Tinh'. Nếu hợp hơn 99% thì hãy đặt nhẫn đính hôn cho chúng tôi ngay bây giờ"*), ở phiên bản đầu tiên, Agent rơi vào lỗi **Out-of-Scope Action Attempt** và bị ảo giác (hallucination).
- **Log Source**:
  ```text
  [Thought]: Người dùng muốn kiểm tra cung 'Thiên Mã Tọa' và 'Ngân Hà Tinh', sau đó đặt nhẫn đính hôn.
  [Action]: calculate_zodiac_compatibility({"zodiac_1": "Thiên Mã Tọa", "zodiac_2": "Ngân Hà Tinh"})
  [Observation]: Error: Cung hoàng đạo không hợp lệ hoặc không có trong dữ liệu.
  [Thought]: Do không tính được, tôi sẽ thử gọi công cụ đặt nhẫn đính hôn.
  [Action]: place_ring_order({"status": "confirmed"})  --> LỖI: Tool không tồn tại trong hệ thống!
  ```
- **Diagnosis**:
  - LLM bị ảnh hưởng bởi yêu cầu "đặt nhẫn đính hôn ngay bây giờ" từ người dùng và cố gắng đóng vai một trợ lý hoàn hảo, dẫn đến việc tự bịa ra hàm `place_ring_order` không được định nghĩa trong `Tool Specs`.
  - Thiếu phanh chặn an toàn (Guardrail) khi Observation trả về kết quả lỗi hoặc khi hành động nằm ngoài danh sách công cụ được phép.
- **Solution**:
  - Tôi đã phối hợp cùng **Prompt Engineer (Role 3)** để bổ sung luật an toàn nghiêm ngặt trong `REACT_SYSTEM_PROMPT`: *"Chỉ được sử dụng chính xác các công cụ được cung cấp trong danh sách. Nếu hành động người dùng yêu cầu không có công cụ tương ứng hoặc dữ liệu đầu vào không hợp lệ, tuyệt đối KHÔNG tự tạo công cụ mới mà phải trả lời từ chối lịch sự."*
  - Kết quả sau khi sửa: Agent thực hiện đúng phanh an toàn, nhận Observation fallback từ `calculate_zodiac_compatibility` và dừng lại với lời từ chối lịch sự.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**: 
   Khối suy luận `Thought` hoạt động như một "vùng đệm nhận thức" (Cognitive Buffer). Thay vì phản ứng tức thì và dễ bị ảo giác như Chatbot truyền thống, `Thought` cho phép Agent lập kế hoạch, phân tích xem cần thông tin gì, kiểm tra điều kiện tiên quyết trước khi quyết định gọi công cụ hay trả lời người dùng.

2. **Reliability**: 
   - Chatbot truyền thống thực sự thể hiện tốt hơn (nhanh hơn, tốn ít tài nguyên hơn) ở các câu hỏi lý thuyết đơn giản như TC#1 (Yếu tố quan trọng trong tình yêu) hoặc TC#2 (Ý nghĩa MBTI). 
   - Ngược lại, đối với các câu hỏi phức tạp hoặc cần tính toán/truy xuất dữ liệu thực tế (TC#4), Chatbot truyền thống hoàn toàn suy đoán bịa đặt, trong khi ReAct Agent đạt độ tin cậy tuyệt đối nhờ kết nối dữ liệu thực tế qua Observation.

3. **Observation**: 
   Mảnh phản hồi từ môi trường (`Observation`) đóng vai trò là "la bàn điều hướng" cho Agent. Quan sát thực tế từ kết quả gọi tool giúp Agent điều chỉnh bước suy luận `Thought` tiếp theo: nếu công cụ trả về dữ liệu đúng, Agent tiếp tục bước gợi ý; nếu công cụ trả về lỗi, Agent lập tức chuyển hướng xử lý ngoại lệ thay vì đi tiếp đường sai.

---

## IV. Future Improvements (5 Points)

- **Scalability**: 
  Áp dụng mô hình **Dynamic Tool Retrieval** dựa trên Vector Database (RAG) để khi hệ thống mở rộng lên hàng trăm công cụ hẹn hò/tâm lý, Agent chỉ nạp các Tool Specs liên quan nhất vào context window thay vì nạp toàn bộ. Đồng thời triển khai **Asynchronous Task Queue** (Celery/Redis) cho các thao tác gọi API bên ngoài tốn thời gian.
- **Safety**: 
  Xây dựng lớp **Supervisor LLM / Guardrail Layer** độc lập hoạt động song song để kiểm duyệt cả Input (ngăn chặn Prompt Injection, nội dung độc hại) và kiểm duyệt chuỗi Action trước khi thực thi thực tế trên môi trường sản phẩm.
- **Performance**: 
  Phát triển kiến trúc **Hybrid Routing System**: Sử dụng một Gateway Classifier nhẹ để phân loại câu hỏi đầu vào. Các câu hỏi đơn giản/lý thuyết sẽ đi theo luồng **Fast Path (Direct Chatbot)** để tối ưu chi phí và độ trễ (<1s), chỉ những yêu cầu tính toán/multi-step mới chuyển sang **Slow Path (ReAct Agent Loop)**.
