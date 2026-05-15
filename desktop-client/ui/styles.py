PRIMARY = "#00d4ff"
PRIMARY_DIM = "rgba(0,212,255,0.3)"
PRIMARY_GLOW = "rgba(0,212,255,0.15)"
BG_DARK = "#0a0e17"
BG_CARD = "rgba(255,255,255,0.03)"
BG_GLASS = "rgba(255,255,255,0.05)"
BG_GLASS_STRONG = "rgba(255,255,255,0.08)"
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#8899aa"
TEXT_DIM = "#556677"
SUCCESS = "#00ff88"
WARNING = "#ffaa00"
DANGER = "#ff3366"
BORDER_GLOW = "rgba(0,212,255,0.3)"
BORDER_SUBTLE = "rgba(255,255,255,0.06)"

DARK_STYLESHEET = f"""
QMainWindow {{
    background-color: {BG_DARK};
}}
QWidget {{
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
}}
QLabel {{
    color: {TEXT_PRIMARY};
    background: transparent;
    border: none;
}}
QLabel#titleLabel {{
    font-size: 18px;
    font-weight: 700;
    color: {PRIMARY};
    letter-spacing: 3px;
}}
QLabel#statusLabel {{
    font-size: 12px;
    color: {TEXT_SECONDARY};
}}
QLabel#fpsLabel {{
    font-size: 14px;
    font-weight: 600;
    color: {SUCCESS};
}}
QLabel#resolutionLabel {{
    font-size: 12px;
    color: {TEXT_SECONDARY};
}}
QLabel#deviceLabel {{
    font-size: 12px;
    color: {TEXT_SECONDARY};
}}
QLabel#sectionTitle {{
    font-size: 13px;
    font-weight: 600;
    color: {PRIMARY};
    padding: 4px 0px;
}}
QLabel#hudText {{
    font-size: 11px;
    color: {PRIMARY};
    background: {BG_GLASS};
    border: 1px solid {BORDER_GLOW};
    border-radius: 4px;
    padding: 4px 10px;
}}
QPushButton {{
    background: {BG_GLASS};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 8px;
    padding: 10px 22px;
    font-size: 13px;
    font-weight: 500;
    min-height: 20px;
}}
QPushButton:hover {{
    background: {BG_GLASS_STRONG};
    border: 1px solid {BORDER_GLOW};
}}
QPushButton:pressed {{
    background: {PRIMARY_DIM};
}}
QPushButton#connectBtn {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #00d4ff, stop:1 #0088cc);
    color: {BG_DARK};
    font-weight: 700;
    border: none;
    border-radius: 8px;
    padding: 12px 30px;
    font-size: 14px;
}}
QPushButton#connectBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #33ddff, stop:1 #0099dd);
}}
QPushButton#connectBtn:disabled {{
    background: {BG_GLASS};
    color: {TEXT_DIM};
}}
QPushButton#dangerBtn {{
    color: {DANGER};
    border: 1px solid {DANGER};
}}
QPushButton#dangerBtn:hover {{
    background: rgba(255,51,102,0.1);
}}
QPushButton#iconBtn {{
    background: {BG_GLASS};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 8px;
    padding: 8px;
    min-width: 36px;
    min-height: 36px;
    font-size: 18px;
}}
QPushButton#iconBtn:hover {{
    background: {BG_GLASS_STRONG};
    border: 1px solid {BORDER_GLOW};
}}
QPushButton#iconBtnActive {{
    background: rgba(0,212,255,0.15);
    border: 1px solid {PRIMARY};
}}
QPushButton#recordBtn {{
    background: rgba(255,51,102,0.15);
    border: 2px solid {DANGER};
    border-radius: 8px;
    padding: 8px 16px;
    color: {DANGER};
    font-weight: 600;
}}
QPushButton#recordBtn:hover {{
    background: rgba(255,51,102,0.25);
}}
QPushButton#recordBtnActive {{
    background: {DANGER};
    color: white;
}}
QPushButton#settingsBtn {{
    background: transparent;
    border: none;
    font-size: 20px;
    padding: 4px;
    color: {TEXT_SECONDARY};
}}
QPushButton#settingsBtn:hover {{
    color: {PRIMARY};
}}
QLineEdit {{
    background: {BG_GLASS};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 13px;
}}
QLineEdit:focus {{
    border: 1px solid {PRIMARY};
    background: rgba(0,212,255,0.05);
}}
QSpinBox, QComboBox {{
    background: {BG_GLASS};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
}}
QSpinBox:focus, QComboBox:focus {{
    border: 1px solid {PRIMARY};
}}
QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}
QComboBox::down-arrow {{
    image: none;
    border: none;
}}
QComboBox QAbstractItemView {{
    background: #111822;
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_GLOW};
    border-radius: 4px;
    selection-background-color: {PRIMARY_DIM};
}}
QCheckBox {{
    spacing: 10px;
    font-size: 13px;
    color: {TEXT_SECONDARY};
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {BORDER_SUBTLE};
    border-radius: 4px;
    background: transparent;
}}
QCheckBox::indicator:checked {{
    background: {PRIMARY};
    border-color: {PRIMARY};
}}
QCheckBox::indicator:hover {{
    border-color: {PRIMARY};
}}
QSlider::groove:horizontal {{
    border: none;
    height: 4px;
    background: {BG_GLASS};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {PRIMARY};
    border: none;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}
QSlider::sub-page:horizontal {{
    background: {PRIMARY};
    border-radius: 2px;
}}
QProgressBar {{
    background: {BG_GLASS};
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #00d4ff, stop:1 #0088cc);
    border-radius: 4px;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BG_GLASS_STRONG};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QGroupBox {{
    font-size: 13px;
    font-weight: 600;
    color: {PRIMARY};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 8px;
    margin-top: 12px;
    padding: 16px 12px 12px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 10px;
    background: {BG_DARK};
}}
QDialog {{
    background: {BG_DARK};
}}
QMenu {{
    background: #111822;
    border: 1px solid {BORDER_GLOW};
    border-radius: 8px;
    padding: 4px;
}}
QMenu::item {{
    padding: 8px 24px;
    border-radius: 4px;
    font-size: 13px;
}}
QMenu::item:selected {{
    background: {PRIMARY_DIM};
    color: {TEXT_PRIMARY};
}}
"""

GLASS_STYLESHEET = """
QWidget#glassCard {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(0,212,255,0.15);
    border-radius: 12px;
}
QWidget#glassCard:hover {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(0,212,255,0.3);
}
"""

BUTTON_STYLES = {
    "connect": f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #00d4ff, stop:1 #0088cc);
            color: #0a0e17;
            font-weight: 700;
            border: none;
            border-radius: 8px;
            padding: 12px 30px;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #33ddff, stop:1 #0099dd);
        }}
    """,
    "danger": f"""
        QPushButton {{
            background: rgba(255,51,102,0.15);
            border: 2px solid {DANGER};
            border-radius: 8px;
            padding: 8px 20px;
            color: {DANGER};
            font-weight: 600;
            font-size: 13px;
        }}
        QPushButton:hover {{
            background: rgba(255,51,102,0.25);
        }}
    """,
    "glass": f"""
        QPushButton {{
            background: {BG_GLASS};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER_SUBTLE};
            border-radius: 8px;
            padding: 10px 22px;
            font-size: 13px;
        }}
        QPushButton:hover {{
            background: {BG_GLASS_STRONG};
            border: 1px solid {BORDER_GLOW};
        }}
    """,
}
