from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QWidget,
    QGroupBox,
    QCheckBox,
    QSlider,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QFileDialog,
    QGridLayout,
    QFrame,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont

from ui.styles import DARK_STYLESHEET, PRIMARY, BG_DARK, BG_GLASS, TEXT_SECONDARY
from utils.helpers import load_settings, save_settings


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RifatCam Pro - Settings")
        self.setMinimumSize(650, 520)
        self.setMaximumSize(900, 700)
        self.setModal(True)
        self.setStyleSheet(self._dialog_style())

        self._settings = load_settings()
        self._build_ui()

    def _dialog_style(self):
        return f"""
            QDialog {{
                background-color: {BG_DARK};
                border: 1px solid rgba(0,212,255,0.3);
                border-radius: 12px;
            }}
            QTabWidget::pane {{
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(0,212,255,0.15);
                border-radius: 8px;
                padding: 16px;
            }}
            QTabBar::tab {{
                background: rgba(255,255,255,0.03);
                color: {TEXT_SECONDARY};
                border: none;
                padding: 12px 24px;
                font-size: 13px;
                font-weight: 500;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            QTabBar::tab:selected {{
                background: rgba(0,212,255,0.1);
                color: #00d4ff;
                border-bottom: 2px solid #00d4ff;
            }}
            QTabBar::tab:hover {{
                background: rgba(0,212,255,0.05);
                color: #ffffff;
            }}
            QLabel#sectionHeader {{
                font-size: 15px;
                font-weight: 700;
                color: #00d4ff;
                padding: 8px 0px;
            }}
        """

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("⚙ SETTINGS")
        header.setObjectName("sectionHeader")
        header.setStyleSheet(
            "font-size: 18px; font-weight: 700; color: #00d4ff; letter-spacing: 2px;"
        )
        layout.addWidget(header)

        tabs = QTabWidget()
        tabs.addTab(self._stream_tab(), "Streaming")
        tabs.addTab(self._recording_tab(), "Recording")
        tabs.addTab(self._detection_tab(), "Detection")
        tabs.addTab(self._general_tab(), "General")
        tabs.addTab(self._about_tab(), "About")
        layout.addWidget(tabs)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton("SAVE SETTINGS")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4ff, stop:1 #0088cc);
                color: #0a0e17;
                font-weight: 700;
                border: none;
                border-radius: 8px;
                padding: 12px 32px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #33ddff, stop:1 #0099dd);
            }}
        """)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("CANCEL")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,255,255,0.05);
                color: #8899aa;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 12px 32px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.08);
                color: #ffffff;
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def _stream_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        grp = QGroupBox("Stream Settings")
        grid = QGridLayout()

        row = 0
        grid.addWidget(QLabel("Preferred Resolution:"), row, 0)
        self._res_combo = QComboBox()
        self._res_combo.addItems(
            ["480p (640x480)", "720p (1280x720)", "1080p (1920x1080)"]
        )
        self._res_combo.setCurrentText(
            {
                "480p": "480p (640x480)",
                "720p": "720p (1280x720)",
                "1080p": "1080p (1920x1080)",
            }.get(self._settings.get("preferred_resolution", "720p"), "720p (1280x720)")
        )
        grid.addWidget(self._res_combo, row, 1)

        row += 1
        grid.addWidget(QLabel("FPS Limit:"), row, 0)
        self._fps_spin = QSpinBox()
        self._fps_spin.setRange(1, 60)
        self._fps_spin.setValue(self._settings.get("fps_limit", 30))
        grid.addWidget(self._fps_spin, row, 1)

        row += 1
        self._auto_connect_cb = QCheckBox("Auto-connect to last device on startup")
        self._auto_connect_cb.setChecked(self._settings.get("auto_connect", False))
        grid.addWidget(self._auto_connect_cb, row, 0, 1, 2)

        grp.setLayout(grid)
        layout.addWidget(grp)
        layout.addStretch()
        return tab

    def _recording_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        grp = QGroupBox("Recording Settings")
        grid = QGridLayout()

        row = 0
        self._save_screenshots_cb = QCheckBox("Auto-save screenshots")
        self._save_screenshots_cb.setChecked(
            self._settings.get("save_screenshots", True)
        )
        grid.addWidget(self._save_screenshots_cb, row, 0, 1, 2)

        row += 1
        self._save_recordings_cb = QCheckBox("Auto-save recordings")
        self._save_recordings_cb.setChecked(self._settings.get("save_recordings", True))
        grid.addWidget(self._save_recordings_cb, row, 0, 1, 2)

        row += 1
        grid.addWidget(QLabel("Recording Format:"), row, 0)
        self._format_combo = QComboBox()
        self._format_combo.addItems(["MP4 (H.264)", "MP4 (MPEG-4)", "AVI (MJPEG)"])
        format_map = {
            "mp4": "MP4 (H.264)",
            "avc1": "MP4 (H.264)",
            "mp4v": "MP4 (MPEG-4)",
            "mjpg": "AVI (MJPEG)",
        }
        self._format_combo.setCurrentText(
            format_map.get(self._settings.get("recording_format", "mp4"), "MP4 (H.264)")
        )
        grid.addWidget(self._format_combo, row, 1)

        grp.setLayout(grid)
        layout.addWidget(grp)

        dir_grp = QGroupBox("Save Locations")
        dir_layout = QGridLayout()

        dir_layout.addWidget(QLabel("Screenshots:"), 0, 0)
        self._ss_dir_label = QLabel("Default")
        self._ss_dir_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        dir_layout.addWidget(self._ss_dir_label, 0, 1)

        dir_layout.addWidget(QLabel("Recordings:"), 1, 0)
        self._rec_dir_label = QLabel("Default")
        self._rec_dir_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        dir_layout.addWidget(self._rec_dir_label, 1, 1)

        dir_grp.setLayout(dir_layout)
        layout.addWidget(dir_grp)
        layout.addStretch()
        return tab

    def _detection_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        grp = QGroupBox("Motion Detection")
        grid = QGridLayout()

        self._motion_cb = QCheckBox("Enable motion detection")
        self._motion_cb.setChecked(self._settings.get("motion_detection", False))
        grid.addWidget(self._motion_cb, 0, 0, 1, 2)

        grid.addWidget(QLabel("Sensitivity:"), 1, 0)
        self._motion_slider = QSlider(Qt.Orientation.Horizontal)
        self._motion_slider.setRange(1, 100)
        self._motion_slider.setValue(
            int(self._settings.get("motion_sensitivity", 0.5) * 100)
        )
        grid.addWidget(self._motion_slider, 1, 1)

        grp.setLayout(grid)
        layout.addWidget(grp)

        ai_grp = QGroupBox("AI Detection")
        ai_layout = QGridLayout()

        self._ai_cb = QCheckBox("Enable AI detection (face/human)")
        self._ai_cb.setChecked(self._settings.get("enable_ai_detection", False))
        ai_layout.addWidget(self._ai_cb, 0, 0, 1, 2)

        ai_layout.addWidget(
            QLabel("Note: YOLO model files must be placed in ~/.rifatcam/models/"),
            1,
            0,
            1,
            2,
        )

        ai_grp.setLayout(ai_layout)
        layout.addWidget(ai_grp)
        layout.addStretch()
        return tab

    def _general_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        grp = QGroupBox("Display")
        grid = QGridLayout()

        self._show_fps_cb = QCheckBox("Show FPS counter")
        self._show_fps_cb.setChecked(self._settings.get("show_fps", True))
        grid.addWidget(self._show_fps_cb, 0, 0, 1, 2)

        self._notifications_cb = QCheckBox("Enable desktop notifications")
        self._notifications_cb.setChecked(
            self._settings.get("enable_notifications", True)
        )
        grid.addWidget(self._notifications_cb, 1, 0, 1, 2)

        grp.setLayout(grid)
        layout.addWidget(grp)

        net_grp = QGroupBox("Network")
        net_layout = QGridLayout()

        net_layout.addWidget(QLabel("Last Device IP:"), 0, 0)
        self._last_ip = QLineEdit()
        self._last_ip.setText(self._settings.get("last_device_ip", ""))
        self._last_ip.setPlaceholderText("192.168.1.x")
        net_layout.addWidget(self._last_ip, 0, 1)

        net_grp.setLayout(net_layout)
        layout.addWidget(net_grp)
        layout.addStretch()
        return tab

    def _about_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("RifatCam Pro")
        title.setStyleSheet(
            "font-size: 24px; font-weight: 700; color: #00d4ff; letter-spacing: 3px;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        ver = QLabel("Version 1.0.0")
        ver.setStyleSheet(f"font-size: 14px; color: {TEXT_SECONDARY};")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(ver)

        desc = QLabel(
            "Premium Wi-Fi Camera Streaming Software\n"
            "Stream your Android phone camera to your PC\n"
            "over your local network in real-time.\n\n"
            "Built with Python, PyQt6 & OpenCV\n"
            "Android app built with Kotlin & CameraX"
        )
        desc.setStyleSheet(
            f"font-size: 13px; color: {TEXT_SECONDARY}; line-height: 1.6;"
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)

        copyright_label = QLabel("© 2026 RifatCam. All rights reserved.")
        copyright_label.setStyleSheet(
            f"font-size: 11px; color: #556677; margin-top: 20px;"
        )
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copyright_label)

        layout.addStretch()
        return tab

    def get_settings(self):
        res_map = {
            "480p (640x480)": "480p",
            "720p (1280x720)": "720p",
            "1080p (1920x1080)": "1080p",
        }
        fmt_map = {
            "MP4 (H.264)": "mp4",
            "MP4 (MPEG-4)": "mp4v",
            "AVI (MJPEG)": "mjpg",
        }
        return {
            "preferred_resolution": res_map.get(self._res_combo.currentText(), "720p"),
            "fps_limit": self._fps_spin.value(),
            "auto_connect": self._auto_connect_cb.isChecked(),
            "save_screenshots": self._save_screenshots_cb.isChecked(),
            "save_recordings": self._save_recordings_cb.isChecked(),
            "recording_format": fmt_map.get(self._format_combo.currentText(), "mp4"),
            "motion_detection": self._motion_cb.isChecked(),
            "motion_sensitivity": self._motion_slider.value() / 100.0,
            "enable_ai_detection": self._ai_cb.isChecked(),
            "show_fps": self._show_fps_cb.isChecked(),
            "enable_notifications": self._notifications_cb.isChecked(),
            "last_device_ip": self._last_ip.text().strip(),
        }

    def _save(self):
        new_settings = self.get_settings()
        save_settings(new_settings)
        self._settings = new_settings
        self.accept()
