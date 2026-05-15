import os
import sys
import time
import json
import threading
from pathlib import Path

import cv2
import numpy as np

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSplitter,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QApplication,
    QDialog,
    QInputDialog,
    QLineEdit,
    QSizePolicy,
    QStackedWidget,
    QScrollArea,
    QSlider,
)
from PyQt6.QtCore import (
    Qt,
    QTimer,
    pyqtSignal,
    QThread,
    QUrl,
    QRect,
    QSize,
    QPropertyAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
)
from PyQt6.QtGui import (
    QFont,
    QPixmap,
    QImage,
    QColor,
    QPalette,
    QAction,
    QKeySequence,
    QIcon,
    QPainter,
    QPen,
    QBrush,
    QLinearGradient,
    QCursor,
    QScreen,
    QShowEvent,
)

from ui.camera_widget import CameraWidget
from ui.hud_overlay import HUDOverlay
from ui.settings_dialog import SettingsDialog
from ui.styles import DARK_STYLESHEET, PRIMARY, BG_DARK, BG_GLASS, TEXT_SECONDARY
from core.stream_receiver import StreamReceiver
from core.recorder import Recorder, ScreenshotCapture
from core.motion_detector import MotionDetector
from core.network_scanner import NetworkScanner
from utils.helpers import (
    get_local_ip,
    load_settings,
    save_settings,
    get_screenshots_dir,
    get_recordings_dir,
    validate_ip,
    DEFAULT_PORT,
)


class ConnectionWorker(QThread):
    connected = pyqtSignal()
    disconnected = pyqtSignal(str)
    frame_received = pyqtSignal(object)
    info_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._receiver = StreamReceiver()
        self._receiver.set_on_frame(self._on_frame)
        self._receiver.set_on_disconnect(self._on_disconnect)
        self._url = ""
        self._running = False

    def set_url(self, url):
        self._url = url

    def run(self):
        self._running = True
        success = self._receiver.start(self._url)
        if success:
            self.connected.emit()
        while self._running and self._receiver.connected:
            self.msleep(100)
        if self._running:
            self.disconnected.emit("Connection lost")

    def stop(self):
        self._running = False
        self._receiver.stop()

    def get_frame(self):
        return self._receiver.get_frame()

    def get_fps(self):
        return self._receiver.fps

    def get_resolution(self):
        return self._receiver.resolution

    def is_connected(self):
        return self._receiver.connected

    def _on_frame(self, frame):
        self.frame_received.emit(frame)

    def _on_disconnect(self):
        if self._running:
            self.disconnected.emit("Device disconnected")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RifatCam Pro")
        self.setMinimumSize(1200, 800)
        self._settings = load_settings()
        self._connected = False
        self._recording = False
        self._fullscreen_mode = False
        self._stream_url = ""
        self._device_name = "No Device"
        self._current_frame = None

        self._init_components()
        self._build_ui()
        self._setup_shortcuts()
        self._setup_auto_connect()

        self._scan_timer = QTimer(self)
        self._scan_timer.timeout.connect(self._update_ui_state)
        self._scan_timer.start(500)

    def _init_components(self):
        self._stream_worker = ConnectionWorker()
        self._stream_worker.connected.connect(self._on_connected)
        self._stream_worker.disconnected.connect(self._on_disconnected)
        self._stream_worker.frame_received.connect(self._on_frame_received)

        self._recorder = Recorder(get_recordings_dir())
        self._screenshot = ScreenshotCapture(get_screenshots_dir())
        self._motion_detector = MotionDetector(
            sensitivity=self._settings.get("motion_sensitivity", 0.5)
        )
        if self._settings.get("motion_detection", False):
            self._motion_detector.enable()

        self._scanner = NetworkScanner()
        self._scanner.set_on_device_found(self._on_device_found)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self._build_topbar())
        main_layout.addWidget(self._build_content(), 1)
        main_layout.addWidget(self._build_control_bar())

        self.setStyleSheet(DARK_STYLESHEET)

    def _build_topbar(self):
        bar = QFrame()
        bar.setObjectName("glassCard")
        bar.setFixedHeight(56)
        bar.setStyleSheet(f"""
            QFrame#glassCard {{
                background: rgba(255,255,255,0.02);
                border-bottom: 1px solid rgba(0,212,255,0.15);
                border-radius: 0px;
            }}
        """)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 20, 0)

        title = QLabel("◆ RIFATCAM  PRO")
        title.setStyleSheet(f"""
            font-size: 18px; font-weight: 700; color: {PRIMARY};
            letter-spacing: 4px; background: transparent; border: none;
        """)
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        layout.addSpacing(30)

        self._status_light = QLabel("⬤")
        self._status_light.setStyleSheet("color: #556677; font-size: 14px;")
        layout.addWidget(self._status_light)

        self._status_label = QLabel("DISCONNECTED")
        self._status_label.setStyleSheet(
            f"color: #556677; font-size: 11px; font-weight: 600; letter-spacing: 1px;"
        )
        layout.addWidget(self._status_label)

        layout.addSpacing(20)

        self._fps_display = QLabel("FPS: --")
        self._fps_display.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 11px; font-family: Consolas;"
        )
        layout.addWidget(self._fps_display)

        layout.addSpacing(15)

        self._res_display = QLabel("--x--")
        self._res_display.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 11px; font-family: Consolas;"
        )
        layout.addWidget(self._res_display)

        layout.addSpacing(15)

        self._device_display = QLabel()
        self._device_display.setStyleSheet(f"color: {PRIMARY}; font-size: 11px;")
        layout.addWidget(self._device_display)

        layout.addStretch()

        ip_label = QLabel(f"IP: {get_local_ip()}")
        ip_label.setStyleSheet(
            f"color: #556677; font-size: 10px; font-family: Consolas;"
        )
        layout.addWidget(ip_label)

        return bar

    def _build_content(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self._camera_widget = CameraWidget()
        self._camera_widget.setStyleSheet("""
            QWidget {
                background: rgba(255,255,255,0.02);
                border: 1px solid rgba(0,212,255,0.1);
                border-radius: 12px;
            }
        """)
        layout.addWidget(self._camera_widget, 1)

        side_panel = self._build_side_panel()
        layout.addWidget(side_panel)

        return container

    def _build_side_panel(self):
        panel = QFrame()
        panel.setObjectName("glassCard")
        panel.setFixedWidth(260)
        panel.setStyleSheet(f"""
            QFrame#glassCard {{
                background: rgba(255,255,255,0.02);
                border: 1px solid rgba(0,212,255,0.1);
                border-radius: 12px;
                padding: 0px;
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        section_title = QLabel("📡 DEVICES")
        section_title.setStyleSheet(
            f"font-size: 11px; font-weight: 700; color: {TEXT_SECONDARY}; letter-spacing: 2px;"
        )
        layout.addWidget(section_title)

        self._device_list = QListWidget()
        self._device_list.setStyleSheet(f"""
            QListWidget {{
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(0,212,255,0.1);
                border-radius: 8px;
                padding: 4px;
                font-size: 12px;
            }}
            QListWidget::item {{
                padding: 10px 12px;
                border-radius: 6px;
                border-bottom: 1px solid rgba(255,255,255,0.03);
                color: #ccddee;
            }}
            QListWidget::item:selected {{
                background: rgba(0,212,255,0.12);
                color: {PRIMARY};
                border: 1px solid rgba(0,212,255,0.2);
            }}
            QListWidget::item:hover {{
                background: rgba(0,212,255,0.06);
            }}
        """)
        self._device_list.setMinimumHeight(180)
        self._device_list.itemDoubleClicked.connect(self._on_device_selected)
        layout.addWidget(self._device_list)

        scan_btn = QPushButton("🔍 SCAN NETWORK")
        scan_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(0,212,255,0.08);
                color: {PRIMARY};
                border: 1px solid rgba(0,212,255,0.2);
                border-radius: 6px;
                padding: 10px;
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background: rgba(0,212,255,0.15);
            }}
        """)
        scan_btn.clicked.connect(self._scan_devices)
        layout.addWidget(scan_btn)

        manual_btn = QPushButton("⌨ MANUAL CONNECT")
        manual_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,255,255,0.03);
                color: {TEXT_SECONDARY};
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 6px;
                padding: 10px;
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                color: {PRIMARY};
                border: 1px solid rgba(0,212,255,0.2);
            }}
        """)
        manual_btn.clicked.connect(self._manual_connect)
        layout.addWidget(manual_btn)

        layout.addSpacing(16)

        section_title2 = QLabel("📊 STATUS")
        section_title2.setStyleSheet(
            f"font-size: 11px; font-weight: 700; color: {TEXT_SECONDARY}; letter-spacing: 2px;"
        )
        layout.addWidget(section_title2)

        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(0,212,255,0.08);
                border-radius: 8px;
            }}
        """)
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(12, 12, 12, 12)
        status_layout.setSpacing(6)

        self._status_items = {}
        for key in ["Signal", "Latency", "Resolution", "Device"]:
            row = QHBoxLayout()
            k = QLabel(f"{key}:")
            k.setStyleSheet(f"color: #556677; font-size: 11px;")
            v = QLabel("--")
            v.setStyleSheet(
                f"color: {TEXT_SECONDARY}; font-size: 11px; font-family: Consolas;"
            )
            row.addWidget(k)
            row.addStretch()
            row.addWidget(v)
            status_layout.addLayout(row)
            self._status_items[key.lower()] = v

        layout.addWidget(status_frame)
        layout.addStretch()

        return panel

    def _build_control_bar(self):
        bar = QFrame()
        bar.setObjectName("glassCard")
        bar.setFixedHeight(64)
        bar.setStyleSheet(f"""
            QFrame#glassCard {{
                background: rgba(255,255,255,0.02);
                border-top: 1px solid rgba(0,212,255,0.1);
                border-radius: 0px;
            }}
        """)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(8)

        self._connect_btn = QPushButton("CONNECT")
        self._connect_btn.setObjectName("connectBtn")
        self._connect_btn.setFixedWidth(140)
        self._connect_btn.clicked.connect(self._toggle_connection)
        layout.addWidget(self._connect_btn)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet(f"background: rgba(0,212,255,0.1); max-width: 1px;")
        layout.addWidget(sep)

        self._btn_switch = self._make_icon_btn("🔄")
        self._btn_switch.setToolTip("Switch Camera (Front/Back)")
        self._btn_switch.clicked.connect(self._switch_camera)
        layout.addWidget(self._btn_switch)

        self._btn_flash = self._make_icon_btn("⚡")
        self._btn_flash.setToolTip("Toggle Flash")
        self._btn_flash.clicked.connect(self._toggle_flash)
        layout.addWidget(self._btn_flash)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.VLine)
        sep2.setStyleSheet(f"background: rgba(0,212,255,0.1); max-width: 1px;")
        layout.addWidget(sep2)

        self._btn_screenshot = self._make_icon_btn("📷")
        self._btn_screenshot.setToolTip("Take Screenshot")
        self._btn_screenshot.clicked.connect(self._take_screenshot)
        layout.addWidget(self._btn_screenshot)

        self._btn_record = QPushButton("● REC")
        self._btn_record.setObjectName("recordBtn")
        self._btn_record.setFixedWidth(100)
        self._btn_record.clicked.connect(self._toggle_recording)
        layout.addWidget(self._btn_record)

        sep3 = QFrame()
        sep3.setFrameShape(QFrame.Shape.VLine)
        sep3.setStyleSheet(f"background: rgba(0,212,255,0.1); max-width: 1px;")
        layout.addWidget(sep3)

        self._btn_zoom_in = self._make_icon_btn("🔍+")
        self._btn_zoom_in.setToolTip("Zoom In")
        self._btn_zoom_in.clicked.connect(
            lambda: self._camera_widget.set_zoom(self._camera_widget._zoom * 1.2)
        )
        layout.addWidget(self._btn_zoom_in)

        self._btn_zoom_out = self._make_icon_btn("🔍−")
        self._btn_zoom_out.setToolTip("Zoom Out")
        self._btn_zoom_out.clicked.connect(
            lambda: self._camera_widget.set_zoom(self._camera_widget._zoom / 1.2)
        )
        layout.addWidget(self._btn_zoom_out)

        self._btn_zoom_reset = self._make_icon_btn("⊡")
        self._btn_zoom_reset.setToolTip("Reset Zoom")
        self._btn_zoom_reset.clicked.connect(self._camera_widget.reset_view)
        layout.addWidget(self._btn_zoom_reset)

        layout.addStretch()

        self._btn_fullscreen = self._make_icon_btn("⛶")
        self._btn_fullscreen.setToolTip("Fullscreen")
        self._btn_fullscreen.clicked.connect(self._toggle_fullscreen)
        layout.addWidget(self._btn_fullscreen)

        self._btn_settings = self._make_icon_btn("⚙")
        self._btn_settings.setToolTip("Settings")
        self._btn_settings.clicked.connect(self._open_settings)
        layout.addWidget(self._btn_settings)

        return bar

    def _make_icon_btn(self, text):
        btn = QPushButton(text)
        btn.setObjectName("iconBtn")
        btn.setFixedSize(40, 40)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    def _setup_shortcuts(self):
        QAction(
            "Fullscreen", self, shortcut="F11", triggered=self._toggle_fullscreen
        ).setAutoRepeat(False)
        QAction(
            "Screenshot", self, shortcut="F12", triggered=self._take_screenshot
        ).setAutoRepeat(False)
        QAction(
            "Record", self, shortcut="Ctrl+R", triggered=self._toggle_recording
        ).setAutoRepeat(False)
        QAction(
            "Settings", self, shortcut="Ctrl+,", triggered=self._open_settings
        ).setAutoRepeat(False)
        QAction(
            "Escape", self, shortcut="Escape", triggered=self._exit_fullscreen
        ).setAutoRepeat(False)
        QAction(
            "Connect", self, shortcut="Ctrl+D", triggered=self._toggle_connection
        ).setAutoRepeat(False)

    def _setup_auto_connect(self):
        if self._settings.get("auto_connect", False):
            last_ip = self._settings.get("last_device_ip", "")
            if last_ip and validate_ip(last_ip):
                QTimer.singleShot(
                    1500,
                    lambda: self._connect_to(f"http://{last_ip}:{DEFAULT_PORT}/video"),
                )

    def _toggle_connection(self):
        if self._connected:
            self._disconnect()
        else:
            devices = self._scanner.devices
            if devices:
                device = devices[0]
                self._connect_to(f"http://{device['ip']}:{device['port']}/video")
            else:
                self._manual_connect()

    def _manual_connect(self):
        ip, ok = QInputDialog.getText(
            self,
            "Manual Connect",
            "Enter device IP address:",
            QLineEdit.EchoMode.Normal,
            self._settings.get("last_device_ip", "192.168.1."),
        )
        if ok and ip.strip():
            ip = ip.strip()
            if not validate_ip(ip):
                QMessageBox.warning(
                    self, "Invalid IP", "Please enter a valid IP address."
                )
                return
            self._connect_to(f"http://{ip}:{DEFAULT_PORT}/video")

    def _connect_to(self, url):
        if self._connected:
            self._disconnect()
        self._stream_url = url
        self._update_status("CONNECTING", "#ffaa00", "#ffaa00")
        self._connect_btn.setEnabled(False)
        self._connect_btn.setText("CONNECTING...")
        self._stream_worker.set_url(url)
        self._stream_worker.start()

    def _disconnect(self):
        self._stream_worker.stop()
        self._stream_worker.wait(2000)
        self._connected = False
        self._current_frame = None
        self._update_status("DISCONNECTED", "#556677", "#556677")
        self._connect_btn.setText("CONNECT")
        self._connect_btn.setEnabled(True)
        self._camera_widget.set_frame(None)
        self._camera_widget.set_info([])
        self._update_device_list_status()

    def _on_connected(self):
        self._connected = True
        self._update_status("CONNECTED", "#00ff88", "#00ff88")
        self._connect_btn.setText("DISCONNECT")
        self._connect_btn.setEnabled(True)
        self._status_items["signal"].setText("Excellent")
        self._status_items["latency"].setText("< 100ms")
        self._extract_device_info()

    def _on_disconnected(self, reason):
        self._connected = False
        self._current_frame = None
        self._update_status("DISCONNECTED", "#556677", "#556677")
        self._connect_btn.setText("CONNECT")
        self._connect_btn.setEnabled(True)
        self._camera_widget.set_frame(None)
        self._status_items["signal"].setText("--")
        self._status_items["latency"].setText("--")
        if self._recording:
            self._stop_recording()

    def _on_frame_received(self, frame):
        self._current_frame = frame
        self._camera_widget.set_frame(frame)

        if self._motion_detector.enabled:
            self._motion_detector.detect(frame)

        if self._recording:
            self._recorder.write_frame(frame)

    def _extract_device_info(self):
        try:
            import requests

            info_url = self._stream_url.replace("/video", "/info")
            resp = requests.get(info_url, timeout=3)
            if resp.status_code == 200:
                info = resp.json()
                name = info.get("name", "RifatCam Device")
                self._device_name = name
                self._device_display.setText(f"📱 {name}")
                self._status_items["device"].setText(name[:20])
        except Exception:
            pass

    def _on_device_found(self, device):
        name = device.get("name", "RifatCam Device")
        ip = device["ip"]
        port = device.get("port", DEFAULT_PORT)
        item_text = f"📱 {name}\n{ip}:{port}"
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, device)
        existing = False
        for i in range(self._device_list.count()):
            if self._device_list.item(i).text() == item_text:
                existing = True
                break
        if not existing:
            self._device_list.addItem(item)

    def _on_device_selected(self, item):
        device = item.data(Qt.ItemDataRole.UserRole)
        if device:
            ip = device["ip"]
            port = device.get("port", DEFAULT_PORT)
            self._connect_to(f"http://{ip}:{port}/video")

    def _scan_devices(self):
        self._device_list.clear()
        self._status_label.setText("SCANNING...")
        self._scanner.start_discovery()
        threading.Thread(target=self._scan_worker, daemon=True).start()

    def _scan_worker(self):
        self._scanner.scan_subnet()
        QTimer.singleShot(
            0,
            lambda: (
                self._status_label.setText("DISCONNECTED")
                if not self._connected
                else None
            ),
        )

    def _toggle_fullscreen(self):
        if self._fullscreen_mode:
            self._exit_fullscreen()
        else:
            self._fullscreen_mode = True
            self.showFullScreen()
            self._btn_fullscreen.setStyleSheet(f"""
                QPushButton#iconBtn {{
                    background: rgba(0,212,255,0.15);
                    border: 1px solid {PRIMARY};
                }}
            """)

    def _exit_fullscreen(self):
        if self._fullscreen_mode:
            self._fullscreen_mode = False
            self.showNormal()
            self._btn_fullscreen.setObjectName("iconBtn")

    def _toggle_recording(self):
        if self._recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        if self._current_frame is None:
            QMessageBox.warning(self, "No Video", "No video stream to record.")
            return
        h, w = self._current_frame.shape[:2]
        success = self._recorder.start_recording(
            w, h, fps=self._settings.get("fps_limit", 30)
        )
        if success:
            self._recording = True
            self._btn_record.setText("■ STOP")
            self._btn_record.setObjectName("recordBtnActive")
            self._btn_record.setStyleSheet(f"""
                QPushButton {{
                    background: #ff3366;
                    color: white;
                    border: 2px solid #ff3366;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                }}
            """)
        else:
            QMessageBox.warning(self, "Error", "Failed to start recording.")

    def _stop_recording(self):
        result = self._recorder.stop_recording()
        self._recording = False
        self._btn_record.setText("● REC")
        self._btn_record.setObjectName("recordBtn")
        self._btn_record.setStyleSheet("")
        if result and result.get("path"):
            self._show_notification("Recording saved", f"Saved to:\n{result['path']}")

    def _take_screenshot(self):
        if self._current_frame is None:
            QMessageBox.warning(self, "No Video", "No video stream to capture.")
            return
        path = self._screenshot.capture(self._current_frame)
        if path:
            self._show_notification("Screenshot saved", f"Saved to:\n{path}")

    def _switch_camera(self):
        if not self._connected or not self._stream_url:
            return
        base = self._stream_url.replace("/video", "")
        try:
            import requests

            requests.post(
                f"{base}/control", json={"command": "switch_camera"}, timeout=2
            )
        except Exception:
            pass

    def _toggle_flash(self):
        if not self._connected or not self._stream_url:
            return
        base = self._stream_url.replace("/video", "")
        try:
            import requests

            requests.post(
                f"{base}/control", json={"command": "toggle_flash"}, timeout=2
            )
        except Exception:
            pass

    def _open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._settings = dialog.get_settings()
            self._motion_detector.set_sensitivity(
                self._settings.get("motion_sensitivity", 0.5)
            )
            if self._settings.get("motion_detection", False):
                self._motion_detector.enable()
            else:
                self._motion_detector.disable()

    def _update_status(self, text, color, light_color):
        self._status_label.setText(text)
        self._status_label.setStyleSheet(
            f"color: {color}; font-size: 11px; font-weight: 600; letter-spacing: 1px;"
        )
        self._status_light.setStyleSheet(f"color: {light_color}; font-size: 14px;")

    def _update_ui_state(self):
        if self._connected and self._stream_worker.is_connected():
            fps = self._stream_worker.get_fps()
            res = self._stream_worker.get_resolution()
            self._fps_display.setText(f"FPS: {fps}")
            self._res_display.setText(f"{res[0]}x{res[1]}" if res[0] > 0 else "--x--")
            self._status_items["resolution"].setText(
                f"{res[0]}x{res[1]}" if res[0] > 0 else "--"
            )

            info_lines = []
            if res[0] > 0:
                info_lines.append(f"RES: {res[0]}x{res[1]}")
            info_lines.append(f"FPS: {fps}")
            info_lines.append(f"DEVICE: {self._device_name[:20]}")
            self._camera_widget.set_info(info_lines)

    def _update_device_list_status(self):
        for i in range(self._device_list.count()):
            item = self._device_list.item(i)
            device = item.data(Qt.ItemDataRole.UserRole)
            if device:
                ip = device["ip"]
                if self._stream_url and ip in self._stream_url:
                    item.setForeground(QColor(PRIMARY))

    def _show_notification(self, title, message):
        try:
            from PyQt6.QtWidgets import QSystemTrayIcon

            if hasattr(self, "_tray_icon") and self._tray_icon is not None:
                self._tray_icon.showMessage(
                    title, message, QSystemTrayIcon.MessageIcon.Information, 3000
                )
        except Exception:
            pass

    def closeEvent(self, event):
        self._stream_worker.stop()
        self._stream_worker.wait(2000)
        if self._recording:
            self._recorder.stop_recording()
        self._scanner.stop_discovery()
        if self._settings.get("auto_connect", False) and self._connected:
            ip = self._stream_url.split("/")[2].split(":")[0]
            self._settings["last_device_ip"] = ip
            save_settings(self._settings)
        event.accept()
