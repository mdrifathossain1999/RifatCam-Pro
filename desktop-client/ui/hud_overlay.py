from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QLinearGradient, QBrush


class HUDOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)

        self._opacity = 0.85
        self._visible = True
        self._scanlines_opacity = 0.03
        self._info_items = []

        self.setMinimumHeight(60)

    def set_info(self, items):
        self._info_items = items
        self.update()

    def set_hud_visible(self, visible):
        self._visible = visible
        self.update()

    def paintEvent(self, event):
        if not self._visible:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        gradient = QLinearGradient(0, 0, 0, h)
        gradient.setColorAt(0.0, QColor(0, 212, 255, 20))
        gradient.setColorAt(1.0, QColor(0, 212, 255, 0))
        painter.fillRect(0, 0, w, h, gradient)

        painter.setPen(QPen(QColor(0, 212, 255, 60), 1))
        painter.drawLine(0, 0, w, 0)

        if self._info_items:
            x_offset = 20
            for key, value in self._info_items:
                painter.setPen(QColor(136, 153, 170))
                font = QFont("Consolas", 9)
                painter.setFont(font)
                painter.drawText(x_offset, 18, key)

                painter.setPen(QColor(0, 212, 255))
                font2 = QFont("Consolas", 10, QFont.Weight.Bold)
                painter.setFont(font2)
                key_width = painter.fontMetrics().horizontalAdvance(key + "  ") + 4
                painter.drawText(x_offset + 2, 38, value)

                x_offset += (
                    painter.fontMetrics().horizontalAdvance(key + value + "     ") + 20
                )

        painter.end()
