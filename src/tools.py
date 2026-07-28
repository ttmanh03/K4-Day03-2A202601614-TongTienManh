# src/tools.py

def calculate_zodiac_compatibility(zodiac_1: str, zodiac_2: str) -> str:
    """
    Tra cứu độ tương thích giữa hai cung hoàng đạo.
    
    Args:
        zodiac_1 (str): Cung hoàng đạo của người thứ nhất (Ví dụ: 'Bảo Bình', 'Kim Ngưu')
        zodiac_2 (str): Cung hoàng đạo của người thứ hai (Ví dụ: 'Thiên Bình', 'Xử Nữ')
    Returns:
        str: Điểm số tương thích và nhận xét cơ bản.
    """
    z1 = zodiac_1.lower().strip()
    z2 = zodiac_2.lower().strip()
    
    # Bảng dữ liệu giả lập (Mock Matrix)
    matrix = {
        ("bảo bình", "thiên bình"): "95% - Tuyệt vời! Cả hai cùng hệ Khí, giao tiếp cực kỳ ăn ý.",
        ("kim ngưu", "xử nữ"): "90% - Cực kỳ hợp! Cả hai cùng hệ Đất, thích sự ổn định và chân thành.",
        ("sư tử", "bọ cạp"): "55% - Cần nhiều nỗ lực. Cả hai đều có cái tôi lớn, dễ va chạm.",
    }
    
    # Tra cứu 2 chiều
    for (a, b), result in matrix.items():
        if (a in z1 and b in z2) or (b in z1 and a in z2):
            return f"Kết quả phân tích Cung Hoàng Đạo ({zodiac_1} & {zodiac_2}): {result}"
            
    return f"Kết quả phân tích Cung Hoàng Đạo ({zodiac_1} & {zodiac_2}): 75% - Độ tương thích mức trung bình khá. Cần tìm hiểu thêm về tính cách thực tế."


def analyze_mbti_match(mbti_1: str, mbti_2: str) -> str:
    """
    Phân tích độ hợp nhau giữa hai nhóm tính cách MBTI.
    
    Args:
        mbti_1 (str): Nhóm MBTI người thứ nhất (Ví dụ: 'INTJ', 'ENFP')
        mbti_2 (str): Nhóm MBTI người thứ hai (Ví dụ: 'INFJ', 'ENTP')
    Returns:
        str: Đánh giá độ ăn ý về tính cách.
    """
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


def suggest_date_ideas(location: str, budget: str, vibe: str) -> str:
    """
    Gợi ý địa điểm và kịch bản hẹn hò phù hợp.
    
    Args:
        location (str): Thành phố (Ví dụ: 'Hà Nội', 'TP.HCM')
        budget (str): Ngân sách ('tiết kiệm', 'trung bình', 'sang chảnh')
        vibe (str): Phong cách hẹn hò ('lãng mạn', 'năng động', 'chill/nhẹ nhàng')
    Returns:
        str: Danh sách kịch bản buổi hẹn hò.
    """
    loc = location.lower()
    bgt = budget.lower()
    vb = vibe.lower()
    
    if "hà nội" in loc:
        if "lãng mạn" in vb:
            return "Kịch bản hẹn hò Hà Nội (Lãng mạn): 1. Đón nhau ngắm hoàng hôn Hồ Tây -> 2. Ăn tối Pasta/Steak lãng mạn tại Trúc Bạch -> 3. Đi dạo Phố Cổ."
        elif "năng động" in vb:
            return "Kịch bản hẹn hò Hà Nội (Năng động): 1. Đi chơi Tô tượng / Làm gốm Bát Tràng -> 2. Ăn nem nướng Nha Trang -> 3. Đi chill ở Pub nhạc Live."
            
    elif "tp.hcm" in loc or "hồ chí minh" in loc:
        if "chill" in vb or "nhẹ nhàng" in vb:
            return "Kịch bản hẹn hò TP.HCM (Chill): 1. Cà phê rooftop ngắm hoàng hôn Thảo Điền -> 2. Ăn đồ Nhật -> 3. Đi dạo công viên Bờ sông Sài Gòn."
            
    return f"Gợi ý buổi hẹn tại {location} ({vibe} - Ngân sách {budget}): 1. Cà phê không gian đẹp trò chuyện -> 2. Bữa tối nhẹ nhàng -> 3. Đi dạo hóng gió cùng nhau."


# ---------------------------------------------------------
# DICTIONARY ĐĂNG KÝ TOOL (Role 4 sẽ import dict này vào app.py)
# ---------------------------------------------------------
AVAILABLE_TOOLS = {
    "calculate_zodiac_compatibility": calculate_zodiac_compatibility,
    "analyze_mbti_match": analyze_mbti_match,
    "suggest_date_ideas": suggest_date_ideas,
}