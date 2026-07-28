# src/tools.py

def calculate_zodiac_compatibility(zodiac_1: str, zodiac_2: str) -> str:
    """
    Tra cứu điểm số và phân tích độ tương thích giữa hai cung hoàng đạo.

    Args:
        zodiac_1 (str): Tên cung hoàng đạo thứ nhất (Ví dụ: 'Bảo Bình', 'Kim Ngưu')
        zodiac_2 (str): Tên cung hoàng đạo thứ hai (Ví dụ: 'Thiên Bình', 'Xử Nữ')
    Returns:
        str: Điểm số tương thích và nhận xét cơ bản.
    """
    try:
        # Kiểm tra nếu tham số bị rỗng hoặc không phải chuỗi
        if not zodiac_1 or not zodiac_2 or not isinstance(zodiac_1, str) or not isinstance(zodiac_2, str):
            return "Lỗi: Vui lòng cung cấp đầy đủ tên của cả 2 cung hoàng đạo dưới dạng văn bản."

        z1 = zodiac_1.lower().strip()
        z2 = zodiac_2.lower().strip()

        VALID_ZODIACS = [
            "bạch dương", "kim ngưu", "song tử", "cự giải",
            "sư tử", "xử nữ", "thiên bình", "bọ cạp",
            "nhân mã", "ma kết", "bảo bình", "song ngư"
        ]

        # Kiểm tra tính hợp lệ của tên cung hoàng đạo
        invalid_list = []
        if not any(v in z1 for v in VALID_ZODIACS):
            invalid_list.append(zodiac_1)
        if not any(v in z2 for v in VALID_ZODIACS):
            invalid_list.append(zodiac_2)

        if invalid_list:
            return f"Cảnh báo: Tên cung hoàng đạo không hợp lệ hoặc không thuộc 12 cung tiêu chuẩn: {', '.join(invalid_list)}. Vui lòng cung cấp cung hợp lệ (ví dụ: Bảo Bình, Sư Tử...)."

        matrix = {
            ("bảo bình", "thiên bình"): "95% - Tuyệt vời! Cả hai cùng hệ Khí, giao tiếp cực kỳ ăn ý.",
            ("kim ngưu", "xử nữ"): "90% - Cực kỳ hợp! Cả hai cùng hệ Đất, thích sự ổn định và chân thành.",
            ("sư tử", "bọ cạp"): "55% - Cần nhiều nỗ lực. Cả hai đều có cái tôi lớn, dễ va chạm.",
        }
        
        for (a, b), result in matrix.items():
            if (a in z1 and b in z2) or (b in z1 and a in z2):
                return f"Kết quả phân tích Cung Hoàng Đạo ({zodiac_1} & {zodiac_2}): {result}"
                
        return f"Kết quả phân tích Cung Hoàng Đạo ({zodiac_1} & {zodiac_2}): 75% - Độ tương thích mức trung bình khá. Cần tìm hiểu thêm về tính cách thực tế."
    
    except Exception as e:
        # Bắt mọi lỗi phát sinh ngoài dự kiến và trả về chuỗi thông báo thay vì làm crash app
        return f"Không thể tra cứu cung hoàng đạo do lỗi hệ thống: {str(e)}"


def analyze_mbti_match(mbti_1: str, mbti_2: str) -> str:
    """
    Phân tích chi tiết độ ăn ý và sự bù trừ giữa hai nhóm tính cách MBTI.

    Args:
        mbti_1 (str): Mã nhóm tính cách MBTI thứ nhất (Ví dụ: 'INTJ', 'ENFP')
        mbti_2 (str): Mã nhóm tính cách MBTI thứ hai (Ví dụ: 'ENTP', 'ISTJ')
    Returns:
        str: Đánh giá độ hợp nhau và phân tích tương quan tính cách.
    """
    try:
        if not mbti_1 or not mbti_2 or not isinstance(mbti_1, str) or not isinstance(mbti_2, str):
            return "Lỗi: Vui lòng cung cấp đầy đủ 2 nhóm tính cách MBTI (ví dụ: INTJ, ENFP)."

        m1 = mbti_1.upper().strip()
        m2 = mbti_2.upper().strip()
        
        pairs = {
            ("INTJ", "ENFP"): "Độ hợp: 95% (Cặp đôi Bù Trừ Kim Cương) - Một người logic trầm tính, một người năng động giàu cảm hứng.",
            ("INFJ", "ENTP"): "Độ hợp: 90% (Tri kỷ tâm giao) - Thích thảo luận các chủ đề sâu sắc và ý tưởng mới.",
            ("ISTJ", "ESFP"): "Độ hợp: 60% (Trái dấu hút nhau) - Cần kiên nhẫn vì một người rất quy tắc, một người thích tự do."
        }
        
        for (a, b), result in pairs.items():
            if (a == m1 and b == m2) or (b == m1 and a == m2):
                return f"Kết quả MBTI ({m1} vs {m2}): {result}"
                
        return f"Kết quả MBTI ({m1} vs {m2}): Độ hợp khoảng 70-80%. Cần phát huy điểm chung và tôn trọng điểm khác biệt của nhau."
    
    except Exception as e:
        return f"Không thể phân tích MBTI do lỗi hệ thống: {str(e)}"


def suggest_date_ideas(location: str, budget: str, vibe: str) -> str:
    """
    Gợi ý kịch bản và lịch trình hẹn hò chi tiết theo địa điểm, ngân sách và phong cách.

    Args:
        location (str): Địa điểm / Thành phố (Ví dụ: 'Hà Nội', 'TP.HCM')
        budget (str): Mức ngân sách ('tiết kiệm', 'trung bình', 'sang chảnh')
        vibe (str): Phong cách buổi hẹn ('lãng mạn', 'năng động', 'chill/nhẹ nhàng')
    Returns:
        str: Lịch trình hẹn hò gợi ý theo các bước.
    """
    try:
        # Nếu thiếu tham số nào thì trả về thông báo hướng dẫn nhẹ nhàng
        if not location or not budget or not vibe:
            return "Lỗi: Cần cung cấp đủ địa điểm, ngân sách và phong cách (vibe) để gợi ý kịch bản hẹn hò."

        loc = str(location).lower()
        bgt = str(budget).lower()
        vb = str(vibe).lower()
        
        if "hà nội" in loc:
            if "lãng mạn" in vb:
                return "Kịch bản hẹn hò Hà Nội (Lãng mạn): 1. Đón nhau ngắm hoàng hôn Hồ Tây -> 2. Ăn tối Pasta/Steak lãng mạn tại Trúc Bạch -> 3. Đi dạo Phố Cổ."
            elif "năng động" in vb:
                return "Kịch bản hẹn hò Hà Nội (Năng động): 1. Đi chơi Tô tượng / Làm gôm Bát Tràng -> 2. Ăn nem nướng Nha Trang -> 3. Đi chill ở Pub nhạc Live."
                
        elif "tp.hcm" in loc or "hồ chí minh" in loc:
            if "chill" in vb or "nhẹ nhàng" in vb:
                return "Kịch bản hẹn hò TP.HCM (Chill): 1. Cà phê rooftop ngắm hoàng hôn Thảo Điền -> 2. Ăn đồ Nhật -> 3. Đi dạo công viên Bờ sông Sài Gòn."
                
        return f"Gợi ý buổi hẹn tại {location} ({vibe} - Ngân sách {budget}): 1. Cà phê không gian đẹp trò chuyện -> 2. Bữa tối nhẹ nhàng -> 3. Đi dạo hóng gió cùng nhau."
    
    except Exception as e:
        return f"Không thể tạo gợi ý hẹn hò do lỗi hệ thống: {str(e)}"


# ---------------------------------------------------------
# DICTIONARY ĐĂNG KÝ TOOL
# ---------------------------------------------------------
AVAILABLE_TOOLS = {
    "calculate_zodiac_compatibility": calculate_zodiac_compatibility,
    "analyze_mbti_match": analyze_mbti_match,
    "suggest_date_ideas": suggest_date_ideas,
}