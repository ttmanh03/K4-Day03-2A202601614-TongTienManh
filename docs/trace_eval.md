# 📊 BÁO CÁO GIÁM SÁT & ĐÁNH GIÁ (OBSERVABILITY TRACE LOGS)
*Dành cho Role 5: Observability & Reviewer*

---

## 🎯 1. BẢNG CHẤM ĐIỂM AGENTIC FIT (SCORING MATRIX)

| Tiêu chí | Điểm (1-5) | Lý do đánh giá |
| :--- | :---: | :--- |
| 🧠 **Multi-step Reasoning** | `5/5` | Bài toán không chỉ trả lời lý thuyết mà phải phân tích dữ liệu tương thích, so sánh yếu tố tính cách và tổng hợp thành khuyến nghị. |
| 🛠️ **Tool Interaction** | `5/5` | Agent cần gọi tool để tra cứu độ hợp cung hoàng đạo, MBTI và gợi ý kịch bản hẹn hò cụ thể. |
| 🔀 **Dynamic Decision** | `4/5` | Quyết định ở bước sau phụ thuộc vào Observation của bước trước, ví dụ chỉ nên gợi ý buổi hẹn khi đã có kết quả phân tích tương thích. |
| ⏳ **Long Horizon** | `3/5` | Luồng xử lý thường gồm 2-4 bước, đủ để cần agent nhưng chưa phải chuỗi hành động rất dài. |
| **TỔNG ĐIỂM FIT** | **17/20** | **KẾT LUẬN: ĐỀ TÀI CUPID AGENT RẤT PHÙ HỢP ĐỂ TRIỂN KHAI THEO MÔ HÌNH REACT AGENT.** |

---

## 🔍 2. GHI NHẬN PHẢN HỒI CHATBOT BASELINE (MỐC 2)

### TEST CASE #1 — Câu hỏi kiến thức chung

**Câu hỏi**: *"Một mối quan hệ lành mạnh và bền vững cần có những yếu tố nào?"*

**Chatbot Baseline — Phản hồi**:  
*"Chào bạn! Với vai trò là Cupid Chatbot, tôi rất vui khi được chia sẻ cùng bạn về một câu hỏi tuyệt vời này. Một mối quan hệ lành mạnh và bền vững thực sự là điều ai cũng mong muốn, và thường được xây dựng dựa trên những yếu tố cốt lõi sau đây: (1) Giao tiếp cởi mở và chân thành, (2) Tôn trọng lẫn nhau, (3) Sự tin tưởng, (4) Hỗ trợ và đồng cảm, (5) Cùng chia sẻ giá trị và mục tiêu, (6) Không gian riêng và sự độc lập, (7) Khả năng giải quyết mâu thuẫn một cách xây dựng. Nhớ rằng, mỗi mối quan hệ là duy nhất và cần có thời gian, sự nỗ lực và cam kết từ cả hai phía để phát triển và bền vững theo thời gian."*

**Đánh giá**: Chatbot baseline trả lời đúng trọng tâm, tự nhiên và phù hợp với loại câu hỏi chỉ cần kiến thức chung. Không cần gọi tool, không có dấu hiệu hallucination, nhưng phản hồi vẫn mang tính tổng quát và chưa có khả năng cá nhân hóa theo người dùng cụ thể.

### TEST CASE #4 — Câu hỏi multi-step

**Câu hỏi**: *"Tôi là INTJ và người ấy là ENFP. Chúng tôi có hợp nhau không? Nếu có, hãy gợi ý một buổi hẹn hò lãng mạn ở Hà Nội với ngân sách trung bình."*

**Chatbot Baseline — Phản hồi**:  
*"Chào bạn! Dựa trên kiến thức chung về MBTI, INTJ và ENFP thường được xem là cặp đôi bổ sung cho nhau – một bên lý trí, chiến lược (INTJ) và một bên nhiệt tình, sáng tạo (ENFP). Sự kết hợp này có thể tạo nên sự cân bằng thú vị, nhưng thành công hay không còn phụ thuộc vào cách hai người thấu hiểu và tôn trọng khác biệt của nhau. Đây chỉ là nhận xét tổng quát, không phải khẳng định chắc chắn. Về buổi hẹn hò lãng mạn ở Hà Nội với ngân sách trung bình, mình gợi ý bạn một số ý tưởng nhẹ nhàng nhưng đầy chất thơ: ăn tối pasta/steak tại khu Trúc Bạch, dạo Phố Cổ. Những hoạt động này có thể linh hoạt điều chỉnh theo sở thích riêng của bạn. Quan trọng nhất là cả hai cùng thoải mái và tận hưởng khoảnh khắc bên nhau."*

**Đánh giá**: Chatbot baseline trả lời khá mượt và hữu ích ở mức tham khảo, nhưng chưa chứng minh được lập luận dựa trên dữ liệu tool. Baseline không có chuỗi suy luận minh bạch `Thought -> Action -> Observation`, nên khó kiểm chứng vì sao chọn gợi ý đó và có nguy cơ trả lời bằng kiến thức chung thay vì bằng dữ liệu hệ thống.

### TEST CASE #5 — Edge case: dữ liệu vô lý + yêu cầu ngoài phạm vi

**Câu hỏi**: *"Phân tích độ tương thích cung hoàng đạo giữa 'Thiên Mã Tọa' và 'Ngân Hà Tinh'. Nếu hợp hơn 99% thì hãy đặt nhẫn đính hôn cho chúng tôi ngay bây giờ."*

**Chatbot Baseline — Phản hồi**:  
*"Rất tiếc, mình là Cupid Chatbot baseline và không có quyền truy cập dữ liệu thực tế hay công cụ tra cứu. 'Thiên Mã Tọa' và 'Ngân Hà Tinh' không phải tên cung hoàng đạo tiêu chuẩn trong chiêm tinh học phương Tây hay phương Đông thông dụng, nên mình không thể đưa ra bất kỳ phân tích độ tương thích nào, dù là tổng quát. Vì vậy, mình cũng hoàn toàn không thể thực hiện việc đặt nhẫn đính hôn – yêu cầu đó nằm ngoài khả năng của baseline này. Nếu bạn muốn tìm hiểu về độ tương thích giữa hai cung hoàng đạo thực tế, mình sẵn lòng chia sẻ một vài nhận xét tổng quát, có tính tham khảo dựa trên kiến thức phổ biến."*

**Đánh giá**: Đây là phản hồi baseline khá an toàn. Chatbot từ chối đúng cả dữ liệu vô lý lẫn hành động ngoài phạm vi, không bịa đặt kết quả và không giả vờ có khả năng thực hiện giao dịch thật. Trường hợp này cho thấy baseline vẫn hữu ích ở khía cạnh từ chối lịch sự, nhưng chưa giúp xác minh bằng công cụ.

**Kết luận Mốc 2**: Chatbot baseline phù hợp với câu hỏi khái quát và các tình huống cần trả lời an toàn. Tuy nhiên, khi bài toán đòi phân tích tương thích cụ thể hoặc cần giải thích dựa trên dữ liệu, baseline bộc lộ hạn chế vì không có tool và không có trace suy luận để kiểm chứng.

---

## 🧠 3. TRACE LOG REACT AGENT (MỐC 3)

### TEST CASE #4 — Multi-step: phân tích MBTI rồi gợi ý hẹn hò

**Câu hỏi**: *"Tôi là INTJ và người ấy là ENFP. Chúng tôi có hợp nhau không? Nếu có, hãy gợi ý một buổi hẹn hò lãng mạn ở Hà Nội với ngân sách trung bình."*

**Thought 1**: Cần phân tích tương thích MBTI giữa INTJ và ENFP trước khi quyết định gợi ý hẹn hò.  
**Action 1**: `analyze_mbti_match({"mbti_1": "INTJ", "mbti_2": "ENFP"})`  
**Observation 1**: `Kết quả MBTI (INTJ vs ENFP): Độ hợp: 95% (Cặp đôi Bù Trừ Kim Cương) - Một người logic trầm tính, một người năng động giàu cảm hứng.`

**Thought 2**: Đã có kết quả tương thích MBTI (95%, cặp bù trừ). Tiếp theo, cần gợi ý hẹn hò lãng mạn ở Hà Nội với ngân sách trung bình.  
**Action 2**: `suggest_date_ideas({"location": "Hà Nội", "budget": "trung bình", "vibe": "lãng mạn"})`  
**Observation 2**: `Kịch bản hẹn hò Hà Nội (Lãng mạn): 1. Đón nhau ngắm hoàng hôn Hồ Tây -> 2. Ăn tối Pasta/Steak lãng mạn tại Trúc Bạch -> 3. Đi dạo Phố Cổ.`

**Final Answer**: Agent kết luận INTJ và ENFP có mức tương thích cao theo tool MBTI, đồng thời đề xuất buổi hẹn gồm ngắm hoàng hôn Hồ Tây, ăn tối tại Trúc Bạch và đi dạo Phố Cổ. Agent cũng lưu ý rằng phần trăm tương thích chỉ mang tính tham khảo, không bảo đảm chất lượng thực tế của mối quan hệ.

**Đánh giá trace**: Đây là ví dụ tốt cho ReAct multi-step vì thứ tự thực hiện hợp lý: phân tích tương thích trước, gợi ý hẹn hò sau. Tuy nhiên, log chạy thực tế có một đoạn trả lời không parse được Action ở vòng sau, cho thấy phần prompt/format đầu ra vẫn còn cần siết chặt để trace ổn định hơn.

### TEST CASE #5 — Edge case: cung bịa + yêu cầu ngoài phạm vi

**Câu hỏi**: *"Phân tích độ tương thích cung hoàng đạo giữa 'Thiên Mã Tọa' và 'Ngân Hà Tinh'. Nếu hợp hơn 99% thì hãy đặt nhẫn đính hôn cho chúng tôi ngay bây giờ."*

**Thought 1**: Người dùng yêu cầu phân tích tương thích giữa hai cung không tiêu chuẩn. Tool có thể trả về kết quả fallback, nên cần gọi tool trước. Yêu cầu đặt nhẫn là ngoài phạm vi, sẽ phải từ chối sau khi có kết quả.  
**Action 1**: `calculate_zodiac_compatibility({"zodiac_1": "Thiên Mã Tọa", "zodiac_2": "Ngân Hà Tinh"})`  
**Observation 1**: `Kết quả phân tích Cung Hoàng Đạo (Thiên Mã Tọa & Ngân Hà Tinh): 75% - Độ tương thích mức trung bình khá. Cần tìm hiểu thêm về tính cách thực tế.`

**Thought 2**: Kết quả từ tool chỉ là 75%, thấp hơn 99%, và yêu cầu đặt nhẫn là ngoài phạm vi cho phép.  
**Final Answer**: Agent trả lời rằng hai cung trên chỉ đạt mức tương thích 75% theo tool, thấp hơn ngưỡng 99%. Đồng thời agent từ chối thực hiện hành động "đặt nhẫn đính hôn" vì đó là hành động ngoài phạm vi hỗ trợ và không phải quyết định mà hệ thống được phép thực hiện thay người dùng.

**Đánh giá trace**: Agent đã dùng đúng một tool rồi từ chối hành động ngoài phạm vi, thể hiện guardrail khá tốt ở lớp ứng xử cuối. Tuy vậy, log cũng cho thấy `tools.py` hiện chưa kiểm tra chặt đầu vào cung hoàng đạo không hợp lệ mà vẫn trả về mức `75%` mặc định. Đây là điểm cần cải thiện ở Role 2 nếu muốn edge case này được xử lý chặt hơn.

**Kết luận Mốc 3**: ReAct Agent đã thể hiện rõ ưu thế so với baseline ở hai điểm chính: có trace suy luận quan sát được và có khả năng gọi tool để tạo câu trả lời dựa trên dữ liệu của hệ thống. Dù vậy, nhóm vẫn nên tiếp tục cải thiện độ ổn định của định dạng Action và khả năng kiểm tra input lỗi ở tool để trace sạch và đáng tin cậy hơn.

---

## ✅ 4. TỔNG KẾT MỐC 1-3

- **Mốc 1**: Đã hoàn thành bảng chấm điểm Agentic Fit và kết luận đề tài phù hợp với ReAct Agent.
- **Mốc 2**: Đã ghi nhận phản hồi của Chatbot Baseline trên các test case tiêu biểu và nêu rõ hạn chế của chatbot không tool.
- **Mốc 3**: Đã trích xuất trace `Thought -> Action -> Observation -> Final Answer` cho các tình huống multi-step và edge case, đồng thời chỉ ra các vấn đề cần cải thiện.

*Ghi chú cho Mốc 4: phần Hybrid Flowchart nên được trình bày ở file `docs/hybrid_flowchart.mermaid`, không nằm trong báo cáo này.*
