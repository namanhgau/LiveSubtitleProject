import time
import datetime
import os
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QMenu, QApplication
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRect, QPoint
from PyQt5.QtGui import QFont, QPainter, QPen, QColor

class WorkerThread(QThread):
    update_subtitle = pyqtSignal(str)
    request_hide = pyqtSignal()
    request_show = pyqtSignal()

    def __init__(self, ocr_engine, translator, interval):
        super().__init__()
        self.running = True
        self.is_running_scan = False 
        self.rect = QRect(0, 0, 0, 0)
        self.ocr_engine = ocr_engine
        self.translator = translator
        self.interval = interval
        self.last_text = ""

    def run(self):
        while self.running:
            if self.is_running_scan and self.rect.width() > 30:
                self.request_hide.emit()
                time.sleep(0.06) 
                
                x, y, w, h = self.rect.x(), self.rect.y(), self.rect.width(), self.rect.height()
                text = self.ocr_engine.capture_and_read(x, y, w, h)
                
                self.request_show.emit()

                if text and text != self.last_text:
                    self.last_text = text
                    t_str = datetime.datetime.now().strftime('%H:%M:%S')
                    print(f"[LIVE {t_str}] OCR: {text[:30]}...")
                    
                    translated = self.translator.translate(text)
                    self.save_to_txt(text, translated)
                    self.update_subtitle.emit(translated)
            
            time.sleep(self.interval)

    def save_to_txt(self, original, translated):
        if os.access(".", os.W_OK):
            with open("Lich_Su_Dich.txt", "a", encoding="utf-8") as f:
                ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{ts}]\nGoc: {original}\nDich: {translated}\n{'-'*20}\n")

    def update_rect(self, rect):
        self.rect = rect

class SubtitleOverlay(QMainWindow):
    # Tín hiệu thông báo tọa độ đã thay đổi khi người dùng kéo khung
    position_changed = pyqtSignal(QRect)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.label = QLabel()
        self.label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.label.setStyleSheet("""
            QLabel { 
                color: #00FFCC; 
                background-color: rgba(0, 0, 0, 140); 
                border: 1px solid #00FFCC;
                padding: 5px;
                border-radius: 5px;
            }
        """)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.setCentralWidget(self.label)
        
        self.old_pos = None # Lưu vị trí chuột để tính toán delta khi di chuyển

    def display_text(self, text):
        self.label.setText(text)

    # --- TÍNH NĂNG 1: NHẤN GIỮ CHUỘT TRÁI ĐỂ DI CHUYỂN ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
            # Cập nhật lại vùng quét cho WorkerThread
            self.position_changed.emit(self.geometry())

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    # --- TÍNH NĂNG 2: CHUỘT PHẢI ĐỂ COPY ---
    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        copy_action = context_menu.addAction("Sao chép bản dịch")
        
        # Style cho Menu chuột phải cho đẹp
        context_menu.setStyleSheet("""
            QMenu { background-color: #2d2d44; color: white; border: 1px solid #00FFCC; }
            QMenu::item:selected { background-color: #624bff; }
        """)
        
        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        
        if action == copy_action:
            content = self.label.text()
            if content:
                clipboard = QApplication.clipboard()
                clipboard.setText(content)
                print("[INFO] Da sao chep ban dich vao Clipboard.")
                
# Khung vẽ vùng chọn (Giữ nguyên logic vẽ nhưng đổi màu cho đẹp)
class SelectionOverlay(QWidget):
    area_selected = pyqtSignal(QRect)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowState(Qt.WindowFullScreen)
        self.begin = QPoint()
        self.end = QPoint()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.fillRect(self.rect(), QColor(20, 20, 20, 150)) # Nền tối mờ sang trọng
        if not self.begin.isNull() and not self.end.isNull():
            rect = QRect(self.begin, self.end).normalized()
            qp.setCompositionMode(QPainter.CompositionMode_Clear)
            qp.fillRect(rect, Qt.transparent)
            qp.setCompositionMode(QPainter.CompositionMode_SourceOver)
            qp.setPen(QPen(QColor(0, 255, 204), 2, Qt.DashLine)) # Viền xanh đứt đoạn
            qp.drawRect(rect)

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        rect = QRect(self.begin, self.end).normalized()
        if rect.width() > 10:
            self.area_selected.emit(rect)
        self.close()