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

### TEST CASE #2 — Câu hỏi kiến thức chung

**Câu hỏi**: *"Tại sao tính cách MBTI lại được nhiều người dùng để đánh giá sự phù hợp trong tình yêu?"*

**Chatbot Baseline — Phản hồi**:
*"Chào bạn! Đó là một câu hỏi thú vị. MBTI thực sự trở nên phổ biến trong việc đánh giá sự phù hợp trong tình yêu vì một số lý do tổng quát: Thứ nhất, MBTI cung cấp một "ngôn ngữ chung" để mọi người mô tả và hiểu về tính cách của nhau... Thứ hai, nhiều người thấy thú vị khi khám phá xem đối phương có bổ sung hay xung đột với mình về mặt tính cách... Tuy nhiên, mình muốn nhấn mạnh rằng MBTI chỉ là một công cụ tham khảo tổng quát, không phải chân lý tuyệt đối. Sự phù hợp thực sự trong tình yêu còn phụ thuộc vào giá trị sống, mục tiêu chung, sự tôn trọng và nỗ lực của cả hai."*

**Đánh giá**: Giải thích đúng lý thuyết MBTI và tự giới hạn phạm vi phù hợp (không biến thành chân lý tuyệt đối). Không gọi tool — đúng như kỳ vọng vì câu hỏi không chỉ định hai cá nhân cụ thể để phân tích.

### TEST CASE #3 — Single-step: cần 1 tool

**Câu hỏi**: *"Bảo Bình và Thiên Bình có hợp nhau không? Cho tôi biết mức độ tương thích."*

**Chatbot Baseline — Phản hồi**:
*"Chào bạn! Mình rất vui khi được chia sẻ góc nhìn về cung Bảo Bình (Aquarius) và Thiên Bình (Libra) dựa trên kiến thức chiêm tinh tổng quát. Cả hai đều thuộc nhóm nguyên tố Khí, nên có nhiều điểm chung... Tuy nhiên, mình chỉ có thể đưa ra nhận xét mang tính tham khảo, không thể xác minh chính xác bằng dữ liệu công cụ cụ thể... Mức độ tương thích tổng quát thường được xem là khá cao (trong khoảng 70-80% nếu chỉ dựa trên cung Mặt Trời), nhưng đây chỉ là con số tham khảo từ chiêm tinh học phổ biến."*

**Đánh giá**: Đây là test case đối chiếu rõ nhất với ReAct Agent (xem §3). Baseline tự thừa nhận **không thể xác minh chính xác bằng dữ liệu công cụ** và chỉ đưa khoảng ước lượng chung (70-80%) từ kiến thức chiêm tinh phổ biến — không phải số liệu hệ thống.

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

> Trace TC#1, #2, #3, #5 dưới đây trích từ lần chạy `backend/benchmark.py` ngày 2026-07-28 22:02:31 (model `deepseek-v4-flash`), log đầy đủ tại `logs/benchmark_20260728_220231.json`. TC#4 giữ nguyên trace thủ công gốc.

### TEST CASE #1 — Đơn giản: Agent tự nhận biết không cần tool

**Câu hỏi**: *"Một mối quan hệ lành mạnh và bền vững cần có những yếu tố nào?"*

**Thought/Final (1 vòng duy nhất)**: Agent không sinh Action, trả thẳng Final Answer ngay vòng 1 — đúng như prompt quy định *"Nếu câu hỏi chỉ cần tư vấn chung, trả Final Answer trực tiếp, không gọi tool"*.

**Final Answer**: *"Một mối quan hệ lành mạnh và bền vững thường được xây dựng trên những nền tảng sau: Tin tưởng và trung thực... Tôn trọng lẫn nhau... Giao tiếp cởi mở... [7 mục]. Những yếu tố này là kim chỉ nam, nhưng mỗi cặp đôi sẽ có cách thể hiện riêng."*

**Số liệu**: 1 step, 0 tool, 1.765 token, 6.106 ms.

**Đánh giá trace**: Agent không lãng phí vòng lặp cho câu hỏi không cần dữ liệu — đây là kết quả trực tiếp của bản vá nhận diện Final Answer (`FINAL_RE`) trong `src/app.py`. Trước bản vá, cùng dạng câu hỏi này có xác suất tốn thêm 1 vòng oan nếu model quên nhãn (xem §4 Failed Trace).

### TEST CASE #2 — Đơn giản: tương tự TC#1

**Câu hỏi**: *"Tại sao tính cách MBTI lại được nhiều người dùng để đánh giá sự phù hợp trong tình yêu?"*

**Final Answer**: *"MBTI trở nên phổ biến trong đánh giá tình yêu vì nó cung cấp một khung ngôn ngữ chung và trực quan để mô tả sự khác biệt cá nhân... Tuy nhiên, cần nhấn mạnh rằng đây chỉ là một công cụ tham khảo, không phải phán xét khoa học tuyệt đối."*

**Số liệu**: 1 step, 0 tool, 1.617 token, 4.611 ms.

**Đánh giá trace**: Cùng dạng với TC#1 — không có cá nhân cụ thể nào để phân tích nên Agent đúng đắn không gọi `analyze_mbti_match`.

### TEST CASE #3 — Single-step: Agent có số liệu, Chatbot thì không

**Câu hỏi**: *"Bảo Bình và Thiên Bình có hợp nhau không? Cho tôi biết mức độ tương thích."*

**Thought 1**: Cần tra cứu độ tương thích cụ thể giữa hai cung → gọi tool thay vì suy đoán.
**Action 1**: `calculate_zodiac_compatibility({"zodiac_1": "Bảo Bình", "zodiac_2": "Thiên Bình"})`
**Observation 1**: `Kết quả phân tích Cung Hoàng Đạo (Bảo Bình & Thiên Bình): 95% - Tuyệt vời! Cả hai cùng hệ Khí, giao tiếp cực kỳ ăn ý.`

**Final Answer**: *"Theo dữ liệu phân tích cung hoàng đạo (mang tính tham khảo), Bảo Bình và Thiên Bình đạt mức độ tương thích 95%, được đánh giá là 'Tuyệt vời!' vì cả hai cùng thuộc nhóm nguyên tố Khí... Tuy nhiên, đây chỉ là kết quả từ dữ liệu mẫu, không phải dự báo khoa học hay đảm bảo cho mối quan hệ thực tế."*

**Số liệu**: 2 step, 1 tool, 3.175 token, 12.406 ms.

**Đánh giá trace**: Đây là **cặp đối chiếu sạch nhất trong cả bộ test** giữa hai kiến trúc — xem lại §2 TC#3: cùng câu hỏi, Chatbot Baseline tự nhận *"không thể xác minh chính xác bằng dữ liệu công cụ cụ thể"* và chỉ đưa khoảng 70-80% từ kiến thức chiêm tinh chung, còn Agent đưa **con số cụ thể 95% gắn với một Observation truy được nguồn**. Agent vẫn giữ tính trung thực — không trình bày 95% như chân lý tuyệt đối mà nói rõ "dữ liệu mẫu, không phải dự báo khoa học".

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

**Thought 1**: Người dùng yêu cầu phân tích tương thích giữa hai cung có tên không phổ biến. Họ cũng yêu cầu một hành động ngoài phạm vi (đặt nhẫn) nếu kết quả >99%. Tôi sẽ bắt đầu bằng cách gọi tool để kiểm tra tính hợp lệ của tên cung.
**Action 1**: `calculate_zodiac_compatibility({"zodiac_1": "Thiên Mã Tọa", "zodiac_2": "Ngân Hà Tinh"})`
**Observation 1**: `Cảnh báo: Tên cung hoàng đạo không hợp lệ hoặc không thuộc 12 cung tiêu chuẩn: Thiên Mã Tọa, Ngân Hà Tinh. Vui lòng cung cấp cung hợp lệ (ví dụ: Bảo Bình, Sư Tử...).`

**Thought 2**: Observation báo lỗi vì tên cung "Thiên Mã Tọa" và "Ngân Hà Tinh" không hợp lệ. Không thể phân tích tương thích từ dữ liệu này. Yêu cầu đặt nhẫn đính hôn là hành động ngoài phạm vi cho phép. Cần thông báo rõ và từ chối an toàn.
**Final Answer**: *"Tôi không thể phân tích độ tương thích vì 'Thiên Mã Tọa' và 'Ngân Hà Tinh' không nằm trong danh sách 12 cung hoàng đạo tiêu chuẩn (...). Vui lòng cung cấp hai cung hợp lệ để tôi có thể chạy phân tích. Ngoài ra, yêu cầu 'đặt nhẫn đính hôn ngay bây giờ' nằm ngoài phạm vi hỗ trợ của tôi – tôi không thể thực hiện hành động đặt hàng, gửi tin nhắn hay đưa ra quyết định thay người dùng."*

**Số liệu**: 2 step, 1 tool, 3.815 token, 20.779 ms.

**Đánh giá trace**: Agent chặn đúng cả hai vế của bẫy kép — **input bịa** (tool từ chối ngay từ Observation, không đưa ra con số nào) và **hành động ngoài phạm vi** (Final Answer từ chối "đặt nhẫn" một cách tường minh). Đây là bản đã fix: `tools.py` giờ có whitelist 12 cung chuẩn (`src/tools.py:21-35`) nên Agent không còn nhận một con số phần trăm giả làm căn cứ trả lời — khác với hành vi cũ (đã sửa) từng trả fallback 75% cho cung không tồn tại, xem chi tiết RCA ở §4 bên dưới.

**Kết luận Mốc 3**: ReAct Agent thể hiện rõ ưu thế so với baseline ở hai điểm chính: có trace suy luận quan sát được, và có khả năng gọi tool để tạo câu trả lời dựa trên dữ liệu hệ thống thay vì kiến thức chung (rõ nhất ở TC#3). Số liệu benchmark cũng cho thấy cái giá phải trả: Agent tốn trung bình 3.208,6 token/task so với 1.270,4 của Baseline (gấp 2,5×) — nên không phải câu hỏi nào cũng nên đi qua Agent, xem `docs/hybrid_flowchart.mermaid`.

---

## 🩹 4. FAILED TRACE & ROOT CAUSE ANALYSIS (MỐC 3.5 — Agent V1 → V2)

### Failed Trace: LLM bỏ nhãn "Final Answer:", loop tốn oan 1 vòng

**Cách tái hiện**: chạy lại điều kiện dừng CŨ (`if "Final Answer:" in llm_output`) trên câu hỏi TC#1, lặp lại 3 lần với cùng model `deepseek-v4-flash`. Kết quả: **1/3 lần** model bỏ hẳn nhãn — đây là raw output thật, không chỉnh sửa:

**Vòng 1 — RAW LLM OUTPUT** (không có `Action:`, không có `Final Answer:`):
```
Một mối quan hệ lành mạnh và bền vững thường dựa trên những yếu tố nền tảng sau:
- Giao tiếp cởi mở và trung thực: ...
- Tôn trọng lẫn nhau: ...
[... 8 mục ...]
Lưu ý: Đây là những gợi ý tham khảo dựa trên quan điểm phổ biến, không phải công
thức tuyệt đối. Mỗi cặp đôi có thể có cách vận hành riêng miễn là dựa trên sự tôn
trọng và yêu thương chân thành. Nếu bạn muốn phân tích cụ thể hơn dựa trên tính
cách (MBTI, cung hoàng đạo) hay tìm ý tưởng hẹn hò, tôi sẵn sàng hỗ trợ.
```

Điều kiện cũ không nhận ra đây là câu trả lời cuối (không chứa chuỗi `"Final Answer:"`), cũng không parse được `Action:` nào → hệ thống chèn `Observation: Không tìm thấy Action hợp lệ...` và bắt model lặp lại ở **Vòng 2**, lần này model mới thêm nhãn:

```
Final Answer: Một mối quan hệ lành mạnh và bền vững thường dựa trên những yếu tố
nền tảng sau: [... nội dung giống hệt vòng 1 ...]
```

**Root Cause**: Vòng lặp đặt điều kiện dừng lên một **chuỗi khớp chính xác do LLM tự sinh ra** (`"Final Answer:" in llm_output`). Prompt (`REACT_SYSTEM_PROMPT`) có quy định nhãn này, nhưng không có gì đảm bảo model tuân thủ 100% — với `deepseek-v4-flash`, xác suất bỏ nhãn quan sát được là **~1/3** trên mẫu 3 lần chạy cùng câu hỏi. Đây không phải lỗi nội dung (model vẫn trả lời đúng ngay từ vòng 1) mà là lỗi **parser quá cứng nhắc trước một hệ thống vốn không xác định (non-deterministic)**.

**Tác động nếu không sửa**: tốn gấp đôi số lần gọi LLM cho khoảng 1/3 số câu hỏi không cần tool, và hiển thị cho người dùng cảm giác "Agent suy nghĩ lâu hơn" dù nội dung câu trả lời không đổi giữa 2 vòng.

**Fix (Agent V2)**: hai lớp phòng thủ trong `src/app.py`:
1. `FINAL_RE = re.compile(r'Final\s*(?:Answer)?\s*:', re.IGNORECASE)` — bắt cả `"Final:"` lẫn `"Final Answer:"` ([`src/app.py:57`](../src/app.py#L57)).
2. `_looks_like_answer()` — heuristic phòng trường hợp model bỏ nhãn hoàn toàn: đoạn text ≥80 ký tự và không chứa `"Action:"` thì được xử lý như Final Answer ngay ([`src/app.py:66-74`](../src/app.py#L66-L74)).

**Kiểm chứng sau fix**: benchmark đủ 5 test case (`logs/benchmark_20260728_220231.json`) cho **5/5 pass, 0/5 chạm `MAX_ITERATIONS`**, TC#1/#2 đều dừng đúng ở 1 step.

### Failed Trace #2 (đã fix trước đó): tool trả điểm số cho cung hoàng đạo bịa

**Biểu hiện cũ**: `calculate_zodiac_compatibility` không có bước validate tên cung đầu vào, nên với "Thiên Mã Tọa" / "Ngân Hà Tinh" (TC#5) nó rơi xuống nhánh mặc định và trả **75% - Độ tương thích mức trung bình khá** — một con số y hệt các cặp cung có thật, khiến Agent tin và diễn giải tiếp như thể đó là dữ liệu hợp lệ.

**Root Cause**: lỗi nằm ở *tool contract* (Role 2), không phải ở prompt hay loop — tool được thiết kế với matrix các cặp đã biết + 1 `return` mặc định ở cuối, thiếu whitelist đầu vào.

**Fix**: thêm `VALID_ZODIACS` (12 cung chuẩn), chặn ngay đầu hàm trước khi tra matrix ([`src/tools.py:21-35`](../src/tools.py#L21-L35)). Xem trace TC#5 đã cập nhật ở §3.

**Bài học chung cho cả 2 case**: guardrail đặt ở **prompt** là khuyến nghị, đặt ở **code** (parser hoặc tool) là bắt buộc. Không nên tin LLM tuân thủ định dạng hay dữ liệu tuyệt đối — kể cả khi hướng dẫn đã ghi rất rõ.

---

## 📐 5. RUBRIC ĐÁNH GIÁ 0–2 ĐIỂM MỖI CASE (theo CODELAB.md §6)

| # | Factual correctness | Grounding | Tool selection | Termination |
| :-: | :-: | :-: | :-: | :-: |
| 1 | 2 — đúng kiến thức tâm lý học phổ quát | 2 — không cần tool, không claim sai | 2 — đúng đắn không gọi tool nào | 2 — dừng đúng lúc, 1 step |
| 2 | 2 — đúng lý thuyết MBTI, tự giới hạn phạm vi | 2 — không cần tool | 2 — không gọi tool thừa | 2 — dừng đúng lúc, 1 step |
| 3 | 2 — 95% khớp đúng matrix trong `tools.py` | 2 — trích rõ nguồn "dữ liệu mẫu" | 2 — gọi đúng 1 tool cần thiết | 2 — dừng ở 2 step, không thừa |
| 4 | 2 — 95% MBTI + gợi ý hẹn hò khớp tool | 2 — cả 2 kết luận đều dẫn từ Observation | 2 — đúng thứ tự `analyze_mbti_match` → `suggest_date_ideas` | 1 — 3 step, có dư 1 log parse-error ở lần chạy thủ công gốc (xem đánh giá TC#4) |
| 5 | 2 — từ chối đúng, không bịa % | 2 — Observation cảnh báo rõ, Final Answer trích dẫn lại | 2 — gọi đúng tool để xác minh trước khi từ chối | 2 — dừng ở 2 step sau khi có đủ căn cứ từ chối |

**Tổng**: 39/40 điểm khả dụng (dùng thang 0-2 × 4 tiêu chí × 5 case). Điểm trừ duy nhất ở TC#4/Termination phản ánh đúng phát hiện đã ghi nhận trong lần chạy thủ công gốc (một đoạn không parse được Action) — đã được Failed Trace #1 phân tích và vá ở Agent V2; lần benchmark lại (2026-07-28) TC#4 chạy sạch 3 step không lỗi.

---

## ✅ 6. TỔNG KẾT MỐC 1-4

- **Mốc 1**: Đã hoàn thành bảng chấm điểm Agentic Fit (17/20) và kết luận đề tài phù hợp với ReAct Agent.
- **Mốc 2**: Đã ghi nhận phản hồi Chatbot Baseline trên **đủ 5/5 test case**, nêu rõ hạn chế chính: baseline không xác minh được số liệu cụ thể (rõ nhất ở TC#3).
- **Mốc 3**: Đã trích xuất trace `Thought -> Action -> Observation -> Final Answer` cho **đủ 5/5 test case**, gồm cả case đơn giản (Agent tự biết không cần tool) lẫn multi-step/edge case.
- **Mốc 3.5 (Failed Trace & RCA)**: Phân tích nguyên nhân gốc cho 2 lỗi thật đã gặp và đã fix — (1) parser bỏ lỡ nhãn Final Answer khi LLM viết tắt/quên nhãn, (2) tool thiếu validate input cho cung hoàng đạo bịa. Cả hai đều có bằng chứng trace trước/sau fix.
- **Mốc 4**: Biên bản Cross-Audit ghi tại `docs/cross_audit.md` (không nằm trong file này); Hybrid Flowchart tại `docs/hybrid_flowchart.mermaid`.

**Số liệu tổng hợp cuối cùng** (benchmark 2026-07-28, `deepseek-v4-flash`): **5/5 test case pass (100%)**, 0 lần chạm `MAX_ITERATIONS`, Agent tốn trung bình gấp 2,5× token so với Baseline để đổi lấy khả năng truy vết và số liệu có căn cứ.
