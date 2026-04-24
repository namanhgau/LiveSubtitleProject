# main.py
import sys
from PyQt5.QtWidgets import QApplication

# Import cấu hình và các module
import config
from modules.ocr_engine import ScreenReader
from modules.translator import TranslationService
from modules.ui_overlay import SubtitleOverlay, WorkerThread

def main():
    app = QApplication(sys.argv)

    # 1. Khởi tạo Module Đọc chữ (Hỗ trợ đa ngôn ngữ)
    ocr = ScreenReader(
        tesseract_cmd=config.TESSERACT_CMD, 
        languages=config.OCR_LANGUAGES
    )

    # 2. Khởi tạo Module Dịch thuật
    translator = TranslationService(target_lang=config.TARGET_LANGUAGE)

    # 3. Khởi tạo Luồng xử lý ngầm ghép OCR và Dịch
    worker = WorkerThread(
        ocr_engine=ocr, 
        translator=translator, 
        interval=config.SCAN_INTERVAL
    )

    # 4. Khởi tạo và Hiển thị Giao diện
    window = SubtitleOverlay(worker_thread=worker)
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()