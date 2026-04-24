# modules/ocr_engine.py
import cv2
import pytesseract
import numpy as np
from PIL import ImageGrab
import re

class ScreenReader:
    def __init__(self, tesseract_cmd, languages):
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        self.languages = languages

    def capture_and_read(self, x, y, w, h):
        try:
            # 1. Chụp màn hình vùng đã chọn (cộng thêm lề để tránh dính viền khung xanh)
            img = ImageGrab.grab(bbox=(x+5, y+5, x + w - 5, y + h - 5))
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

            # 2. Tiền xử lý ảnh nâng cao
            # Bước A: Chuyển sang ảnh xám
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Bước B: Tăng kích thước ảnh (Upscaling) giúp Tesseract đọc chữ nhỏ tốt hơn
            gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

            # Bước C: Khử nhiễu
            distorted = cv2.fastNlMeansDenoising(gray, h=10)

            # Bước D: Nhị phân hóa thích nghi (Adaptive Thresholding) 
            # Giúp tách chữ ra khỏi nền kể cả khi nền sáng tối không đều
            thresh = cv2.adaptiveThreshold(
                distorted, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )

            # 3. Đọc chữ với cấu hình tối ưu cho Tesseract (PSM 6: Giả định vùng là một khối văn bản)
            custom_config = r'--oem 3 --psm 4' 
            text = pytesseract.image_to_string(thresh, lang=self.languages, config=custom_config).strip()
            
            # Lọc bỏ các ký tự rác thường gặp khi OCR lỗi
            clean_text = self.clean_junk_chars(text)
            return clean_text
            
        except Exception as e:
            print(f"Lỗi đọc màn hình/OCR: {e}")
            return ""
        
    def clean_junk_chars(self, text):
        # 1. Thêm dấu câu Tiếng Trung/Nhật (。，、？！「」【】（）) vào danh sách cho phép
        clean = re.sub(r'[^\w\s.,!?\-:;()\'"/%。，、？！「」【】（）]', '', text)
        
        # 2. Thuật toán ghép dòng (Smart Line Merging)
        lines = clean.split('\n')
        processed_paragraphs = []
        current_paragraph = ""
        
        for line in lines:
            line = " ".join(line.split())
            if not line:
                continue
                
            if current_paragraph != "":
                current_paragraph += " " + line
            else:
                current_paragraph = line
                
            # 3. Thêm nhận diện kết thúc câu bằng dấu chấm/hỏi/chấm than của Châu Á
            if line.endswith(('.', '!', '?', ':', '"', "'", '。', '！', '？', '」')):
                processed_paragraphs.append(current_paragraph)
                current_paragraph = "" 
                
        if current_paragraph != "":
            processed_paragraphs.append(current_paragraph)
            
        return "\n".join(processed_paragraphs)
    
    # Trong file modules/ocr_engine.py, class ScreenReader
    def set_languages(self, new_languages):
        self.languages = new_languages