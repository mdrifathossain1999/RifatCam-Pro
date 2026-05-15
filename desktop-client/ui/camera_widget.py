import cv2
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRect, QPoint
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QFont, QLinearGradient


class CameraWidget(QWidget):
    frame_ready = pyqtSignal(object)
    mouse_clicked = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._frame = None
        self._overlay_text = ""
        self._show_status = True
        self._zoom = 1.0
        self._pan_x = 0
        self._pan_y = 0
        self._dragging = False
        self._drag_start = None
        self._target_fps = 30
        self._frame_count = 0
        self._last_fps_time = 0
        self._current_fps = 0
        self._info_lines = []
        self._show_scanlines = True
        self._show_corners = True

        self.setMinimumSize(640, 480)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(16)

    def set_frame(self, frame):
        self._frame = frame
        self._frame_count += 1
        if self._frame_count >= 30:
            now = cv2.getTickCount()
            if self._last_fps_time > 0:
                elapsed = (now - self._last_fps_time) / cv2.getTickFrequency()
                if elapsed > 0:
                    self._current_fps = int(self._frame_count / elapsed)
            self._last_fps_time = now
            self._frame_count = 0

    def set_overlay(self, text):
        self._overlay_text = text

    def set_info(self, lines):
        self._info_lines = lines

    def set_zoom(self, zoom):
        self._zoom = max(1.0, min(5.0, zoom))
        self.update()

    def reset_view(self):
        self._zoom = 1.0
        self._pan_x = 0
        self._pan_y = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w, h = self.width(), self.height()

        background = QColor(10, 14, 23)
        painter.fillRect(0, 0, w, h, background)

        border_color = QColor(0, 212, 255, 40)
        painter.setPen(QPen(border_color, 1))
        painter.drawRect(1, 1, w - 2, h - 2)

        if self._frame is not None and self._frame.size > 0:
            rgb_frame = cv2.cvtColor(self._frame, cv2.COLOR_BGR2RGB)
            frame_h, frame_w = rgb_frame.shape[:2]

            scaled_w = int(frame_w * self._zoom)
            scaled_h = int(frame_h * self._zoom)

            display_w = min(scaled_w, w)
            display_h = min(scaled_h, h)

            if scaled_w > w or scaled_h > h:
                crop_x = max(0, min(self._pan_x, scaled_w - w))
                crop_y = max(0, min(self._pan_y, scaled_h - h))
                crop_frame = rgb_frame[
                    int(crop_y / self._zoom) : int((crop_y + w) / self._zoom),
                    int(crop_x / self._zoom) : int((crop_x + h) / self._zoom),
                ]
                if crop_frame.size > 0:
                    resized = cv2.resize(
                        crop_frame, (w, h), interpolation=cv2.INTER_LINEAR
                    )
                    h_, w_ = resized.shape[:2]
                    bytes_per_line = 3 * w_
                    qimg = QImage(
                        resized.data,
                        w_,
                        h_,
                        bytes_per_line,
                        QImage.Format.Format_RGB888,
                    )
                    pixmap = QPixmap.fromImage(qimg)
                    painter.drawPixmap(0, 0, pixmap)
            else:
                aspect = frame_w / frame_h
                if w / h > aspect:
                    display_h = h
                    display_w = int(h * aspect)
                else:
                    display_w = w
                    display_h = int(w / aspect)

                x_offset = (w - display_w) // 2
                y_offset = (h - display_h) // 2

                resized = cv2.resize(
                    rgb_frame, (display_w, display_h), interpolation=cv2.INTER_AREA
                )
                bytes_per_line = 3 * display_w
                qimg = QImage(
                    resized.data,
                    display_w,
                    display_h,
                    bytes_per_line,
                    QImage.Format.Format_RGB888,
                )
                pixmap = QPixmap.fromImage(qimg)
                painter.drawPixmap(x_offset, y_offset, pixmap)
        else:
            painter.setPen(QColor(0, 212, 255, 60))
            font = QFont("Segoe UI", 16)
            painter.setFont(font)
            no_signal_text = "NO SIGNAL"
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, no_signal_text)

            font2 = QFont("Segoe UI", 11)
            painter.setFont(font2)
            painter.setPen(QColor(136, 153, 170))
            sub_text = "Connect to a RifatCam device to start streaming"
            painter.drawText(
                QRect(0, h // 2 + 30, w, 40), Qt.AlignmentFlag.AlignCenter, sub_text
            )

        if self._show_scanlines:
            self._draw_scanlines(painter, w, h)

        if self._show_corners:
            self._draw_corner_accents(painter, w, h)

        self._draw_hud_overlay(painter, w, h)

        painter.end()

    def _draw_scanlines(self, painter, w, h):
        painter.setPen(QPen(QColor(0, 212, 255, 6), 1))
        for y in range(0, h, 4):
            painter.drawLine(0, y, w, y)

    def _draw_corner_accents(self, painter, w, h):
        length = 30
        thickness = 2
        color = QColor(0, 212, 255, 100)

        painter.setPen(QPen(color, thickness))

        painter.drawLine(0, 0, length, 0)
        painter.drawLine(0, 0, 0, length)

        painter.drawLine(w - length, 0, w, 0)
        painter.drawLine(w - 1, 0, w - 1, length)

        painter.drawLine(0, h - 1, length, h - 1)
        painter.drawLine(0, h - length, 0, h)

        painter.drawLine(w - length, h - 1, w, h - 1)
        painter.drawLine(w - 1, h - length, w - 1, h)

    def _draw_hud_overlay(self, painter, w, h):
        font = QFont("Consolas", 11)
        painter.setFont(font)

        y_offset = 15
        line_height = 20

        for line in self._info_lines:
            rect = QRect(15, y_offset, 250, line_height)

            bg_rect = QRect(12, y_offset - 2, 250, line_height + 4)
            painter.fillRect(bg_rect, QColor(0, 212, 255, 20))
            painter.setPen(QPen(QColor(0, 212, 255, 40), 1))
            painter.drawRect(bg_rect)

            painter.setPen(QColor(0, 212, 255, 200))
            painter.drawText(
                rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, line
            )
            y_offset += line_height + 2

        if self._current_fps > 0:
            fps_text = f"FPS: {self._current_fps}"
            font2 = QFont("Consolas", 13, QFont.Weight.Bold)
            painter.setFont(font2)

            fps_color = (
                QColor(0, 255, 136) if self._current_fps >= 15 else QColor(255, 170, 0)
            )
            painter.setPen(fps_color)

            fps_rect = QRect(w - 150, h - 40, 135, 28)
            painter.fillRect(fps_rect, QColor(0, 0, 0, 120))
            painter.setPen(QPen(QColor(0, 255, 136, 40), 1))
            painter.drawRect(fps_rect)
            painter.setPen(fps_color)
            painter.drawText(fps_rect, Qt.AlignmentFlag.AlignCenter, fps_text)

        if self._zoom > 1.0:
            zoom_text = f"ZOOM: {self._zoom:.1f}x"
            font3 = QFont("Consolas", 11)
            painter.setFont(font3)
            painter.setPen(QColor(0, 212, 255, 150))
            zoom_rect = QRect(w - 150, h - 70, 135, 24)
            painter.fillRect(zoom_rect, QColor(0, 0, 0, 100))
            painter.drawText(zoom_rect, Qt.AlignmentFlag.AlignCenter, zoom_text)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._zoom > 1.0:
            self._dragging = True
            self._drag_start = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self._dragging and self._drag_start:
            pos = event.position()
            dx = pos.x() - self._drag_start.x()
            dy = pos.y() - self._drag_start.y()
            self._pan_x -= int(dx)
            self._pan_y -= int(dy)
            self._drag_start = pos
            self.update()
        else:
            pos = event.position()
            self.mouse_clicked.emit(int(pos.x()), int(pos.y()))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self._drag_start = None
            self.setCursor(Qt.CursorShape.CrossCursor)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.set_zoom(self._zoom * 1.1)
        else:
            self.set_zoom(self._zoom / 1.1)
        event.accept()

    def enterEvent(self, event):
        self.setFocus()

    def leaveEvent(self, event):
        pass
