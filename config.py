# config.py

# 1. Giữ nguyên đường dẫn nếu máy bạn đã cài ở đây
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 2. TỐI ƯU: Nếu bạn chỉ đang dịch web tiếng Anh, hãy để 'eng' thôi để máy quét NHANH hơn.
# Chỉ khi nào xem phim Nhật/Trung thì mới bật full combo này nhé.
OCR_LANGUAGES = 'eng+chi_sim+chi_tra+jpn'

# 3. Đảm bảo đây là chữ thường 'vi'
TARGET_LANGUAGE = 'vi'

# 4. TỐI ƯU: 1.5 giây hơi chậm cho phụ đề, bạn nên thử 0.5 hoặc 0.8 để thấy chữ nhảy nhanh hơn
SCAN_INTERVAL = 0.8