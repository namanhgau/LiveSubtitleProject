# main_gui.py
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QComboBox, QPushButton, QGroupBox, QFrame)
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QFont, QColor

import config
from modules.ocr_engine import ScreenReader
from modules.translator import TranslationService
from modules.ui_overlay import SubtitleOverlay, WorkerThread, SelectionOverlay

class ControlPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        # Khởi tạo core
        self.ocr = ScreenReader(config.TESSERACT_CMD, config.OCR_LANGUAGES)
        self.translator = TranslationService(config.TARGET_LANGUAGE)
        self.worker = WorkerThread(self.ocr, self.translator, config.SCAN_INTERVAL)
        
        self.display = SubtitleOverlay()
        
        # Kết nối tín hiệu
        self.worker.update_subtitle.connect(self.display.display_text)
        self.worker.request_hide.connect(self.display.hide)
        self.worker.request_show.connect(self.display.show)
        self.worker.start()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("NCKH - Subtitle Overlay Pro")
        self.setFixedSize(380, 400)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        # QSS - Làm đẹp giao diện
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e2d; }
            QLabel { color: #a9a9b3; font-size: 13px; }
            QGroupBox { 
                color: #00ffcc; font-weight: bold; 
                border: 1px solid #33334d; border-radius: 8px; margin-top: 15px; 
            }
            QComboBox { 
                background-color: #2d2d44; color: white; border: 1px solid #33334d; 
                border-radius: 4px; padding: 5px; 
            }
            QPushButton { 
                border-radius: 6px; font-weight: bold; font-size: 14px; padding: 10px;
            }
            #btn_draw { background-color: #624bff; color: white; }
            #btn_draw:hover { background-color: #7c69ff; }
            #btn_start { background-color: #00c853; color: white; }
            #btn_start:hover { background-color: #2ef37e; }
            #btn_stop { background-color: #ff3d00; color: white; }
        """)

        container = QWidget()
        layout = QVBoxLayout()

        header = QLabel("TRANSLATOR OVERLAY")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: white; letter-spacing: 2px;")
        layout.addWidget(header)

        # Ngôn ngữ
        lang_group = QGroupBox("Cấu hình Ngôn ngữ")
        lang_lay = QVBoxLayout()
        
        h1 = QHBoxLayout(); h1.addWidget(QLabel("Nguồn:")); self.cb_src = QComboBox()
        self.cb_src.addItem("Đa ngôn ngữ", "eng+chi_sim+jpn")
        self.cb_src.addItem("Tiếng Anh", "eng"); self.cb_src.addItem("Tiếng Nhật", "jpn")
        self.cb_src.currentIndexChanged.connect(lambda: self.ocr.set_languages(self.cb_src.currentData()))
        h1.addWidget(self.cb_src); lang_lay.addLayout(h1)

        lang_group.setLayout(lang_lay)
        layout.addWidget(lang_group)

        # Nút bấm
        self.btn_select = QPushButton("✂  VẼ VÙNG QUÉT")
        self.btn_select.setObjectName("btn_draw")
        self.btn_select.clicked.connect(self.start_selection)
        layout.addWidget(self.btn_select)

        self.btn_toggle = QPushButton("▶  BẮT ĐẦU DỊCH")
        self.btn_toggle.setObjectName("btn_start")
        self.btn_toggle.clicked.connect(self.toggle_scan)
        self.btn_toggle.setEnabled(False)
        layout.addWidget(self.btn_toggle)

        # Line phân cách
        line = QFrame(); line.setFrameShape(QFrame.HLine); line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #33334d;")
        layout.addWidget(line)

        self.lbl_status = QLabel("Trạng thái: Chưa chọn vùng")
        self.lbl_status.setStyleSheet("color: #707080; font-style: italic;")
        layout.addWidget(self.lbl_status)

        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_selection(self):
        self.hide()
        self.sel = SelectionOverlay()
        self.sel.area_selected.connect(self.apply_area)
        self.sel.show()

    def apply_area(self, rect):
        self.show()
        self.worker.update_rect(rect)
        self.display.setGeometry(rect) # Làm khung dịch khớp khít vùng quét
        self.display.position_changed.connect(self.worker.update_rect)
        self.lbl_status.setText(f"Đã chọn vùng: {rect.width()}x{rect.height()}")
        self.btn_toggle.setEnabled(True)
        self.display.show()

    def toggle_scan(self):
        if self.worker.is_running_scan:
            self.worker.is_running_scan = False
            self.btn_toggle.setText("▶  TIẾP TỤC DỊCH")
            self.btn_toggle.setObjectName("btn_start")
            self.btn_toggle.setStyle(self.style())
        else:
            self.worker.is_running_scan = True
            self.btn_toggle.setText("⏸  TẠM DỪNG")
            self.btn_toggle.setObjectName("btn_stop")
            self.btn_toggle.setStyle(self.style())

    def closeEvent(self, event):
        self.worker.running = False
        self.worker.wait()
        self.display.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    panel = ControlPanel()
    panel.show()
    sys.exit(app.exec_())