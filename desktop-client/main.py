#!/usr/bin/env python3
import sys
import os

os.environ["QT_QUICK_CONTROLS_STYLE"] = "material"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont
except ImportError:
    print("=" * 60)
    print("  RifatCam Pro - Dependency Error")
    print("=" * 60)
    print()
    print("  PyQt6 is required but not installed.")
    print()
    print("  Install dependencies with:")
    print("    pip install -r requirements.txt")
    print()
    print("=" * 60)
    sys.exit(1)

from ui import MainWindow
from utils.helpers import APP_NAME, APP_VERSION


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("RifatCam")

    font = QFont("Segoe UI", 10)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)

    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
