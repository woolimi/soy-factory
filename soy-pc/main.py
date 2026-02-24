import os
import sys

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow


def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui_path = os.path.join(os.path.dirname(__file__), "soy-pc.ui")
    uic.loadUi(ui_path, window)
    window.setWindowTitle("SoyAdmin")
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
