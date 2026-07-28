"""
🤖 CẤP ĐỘ 1: RULE-BASED BOT (Chatbot dựa trên luật if/else & regex cố định)
Khớp từ khóa (Keyword/Pattern Matching). Không dùng LLM, 0 tốn API Token.
"""

import re

def rule_based_bot(user_input: str) -> str:
    text = user_input.lower().strip()

    # Rule 1: Chào hỏi
    if any(k in text for k in ["chào", "hi", "hello", "xin chào"]):
        return "🤖 [Rule-Based Bot - Cấp 1]: Xin chào! Tôi là Bot tư vấn cố định (If/Else). Tôi chỉ trả lời các từ khóa cài đặt sẵn."

    # Rule 2: Tra cứu Cung Hoàng Đạo
    if "bảo bình" in text and "thiên bình" in text:
        return "🤖 [Rule-Based Bot - Cấp 1]: 95% - Tuyệt vời! Cả hai cùng hệ Khí, giao tiếp ăn ý (Dữ liệu từ bảng mã cứng)."
    elif "kim ngưu" in text and "xử nữ" in text:
        return "🤖 [Rule-Based Bot - Cấp 1]: 90% - Cực kỳ hợp! Cả hai cùng hệ Đất, thích sự ổn định (Dữ liệu mã cứng)."
    elif "cung" in text or "hoàng đạo" in text:
        return "🤖 [Rule-Based Bot - Cấp 1]: Tôi chỉ có luật mã cứng cho cặp (Bảo Bình - Thiên Bình) và (Kim Ngưu - Xử Nữ)!"

    # Rule 3: MBTI
    if "intj" in text and "enfp" in text:
        return "🤖 [Rule-Based Bot - Cấp 1]: INTJ và ENFP là cặp bù trừ tốt (Khớp từ khóa MBTI)."
    elif "mbti" in text:
        return "🤖 [Rule-Based Bot - Cấp 1]: Tôi chỉ nhận diện được cặp INTJ - ENFP!"

    # Rule 4: Gợi ý hẹn hò Hà Nội
    if "hà nội" in text or "hẹn hò" in text:
        return "🤖 [Rule-Based Bot - Cấp 1]: Gợi ý cố định: Đi dạo Hồ Tây -> Ăn tối Phố Cổ."

    # Fallback khi ngoài tập từ khóa
    return "🤖 [Rule-Based Bot - Cấp 1]: ⚠️ Lỗi! Câu hỏi của bạn nằm ngoài tập luật (keywords) được cài đặt sẵn."


if __name__ == "__main__":
    print("==================================================")
    print("🤖 DEMO CẤP ĐỘ 1: RULE-BASED BOT (ZERO LLM)")
    print("==================================================")
    test_queries = [
        "Xin chào bot",
        "Bảo Bình và Thiên Bình có hợp nhau không?",
        "Gợi ý hẹn hò ở Hà Nội",
        "Thiên Mã Tọa và Ngân Hà Tinh"
    ]
    for q in test_queries:
        print(f"\n💬 Query: {q}")
        print(rule_based_bot(q))
