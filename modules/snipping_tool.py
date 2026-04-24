# modules/snipping_tool.py
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor

class SnippingWidget(QWidget):
    # Tín hiệu phát ra khi người dùng vẽ xong (trả về x, y, chiều rộng, chiều cao)
    on_snip_completed = pyqtSignal(int, int, int, int)

    def __init__(self):
        super().__init__()
        # Tạo cửa sổ toàn màn hình, mờ mờ, luôn nổi trên cùng
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Lấy kích thước toàn bộ màn hình
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.setCursor(Qt.CrossCursor) # Đổi con trỏ chuột thành dấu cộng
        
        self.start_point = None
        self.end_point = None

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Phủ một lớp màu đen mờ lên toàn màn hình để tạo hiệu ứng "đóng băng"
        dim_color = QColor(0, 0, 0, 120) 
        painter.fillRect(self.rect(), dim_color)
        
        # Nếu đang kéo chuột, vẽ một hình chữ nhật trong suốt (vùng chọn) có viền đỏ
        if self.start_point and self.end_point:
            selection_rect = QRect(self.start_point, self.end_point).normalized()
            
            # Làm trong suốt vùng bên trong ô chữ nhật
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(selection_rect, Qt.transparent)
            
            # Vẽ viền đỏ xung quanh
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            pen = QPen(QColor(255, 0, 0), 2, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawRect(selection_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.end_point = self.start_point
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.end_point = event.pos()
            self.update() # Vẽ lại liên tục khi kéo chuột

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.start_point:
            selection_rect = QRect(self.start_point, self.end_point).normalized()
            # Chỉ xử lý nếu vùng vẽ đủ lớn (tránh việc lỡ click nhầm)
            if selection_rect.width() > 10 and selection_rect.height() > 10:
                self.on_snip_completed.emit(
                    selection_rect.x(), selection_rect.y(), 
                    selection_rect.width(), selection_rect.height()
                )
            self.close() # Đóng công cụ vẽ sau khi xong