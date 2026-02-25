import os
import sys

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QFrame, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class AlertMessage(QFrame):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            AlertMessage {
                background-color: #ffebee;
                border: 1px solid #ffcdd2;
                border-radius: 5px;
                margin-bottom: 5px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        icon_label = QLabel("⚠️")
        icon_label.setStyleSheet("font-size: 16px; color: #d32f2f; border: none;")
        
        msg_label = QLabel(message)
        msg_label.setStyleSheet("color: #b71c1c; font-size: 14px; font-weight: bold; border: none;")
        msg_label.setWordWrap(True)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("border: none; color: #d32f2f; font-weight: bold; background-color: transparent;")
        close_btn.clicked.connect(self.deleteLater)
        
        layout.addWidget(icon_label)
        layout.addWidget(msg_label, stretch=1)
        layout.addWidget(close_btn)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), "soy-pc.ui")
        uic.loadUi(ui_path, self)
        
        # Initialize default state
        self.label_pause.setVisible(False)
        self.alert_panel.hide()
        self.main_stack.setCurrentWidget(self.page_standby)
        
        # Connect signals
        self.btn_worker.clicked.connect(self.show_worker_screen)
        self.btn_manager.clicked.connect(self.show_manager_login)
        self.btn_worker_back.clicked.connect(self.show_standby_screen)
        self.btn_manager_back.clicked.connect(self.show_standby_screen)
        self.btn_login.clicked.connect(self.show_manager_dashboard)
        self.btn_logout.clicked.connect(self.show_standby_screen)
        self.btn_toggle_pause.clicked.connect(self.toggle_pause)
        self.btn_test_alert.clicked.connect(self.add_test_alert)
        
    def show_standby_screen(self):
        self.main_stack.setCurrentWidget(self.page_standby)
        self.alert_panel.hide()

    def show_worker_screen(self):
        self.main_stack.setCurrentWidget(self.page_worker)
        self.alert_panel.show()

    def show_manager_login(self):
        self.main_stack.setCurrentWidget(self.page_manager_login)
        self.alert_panel.hide()

    def show_manager_dashboard(self):
        self.input_password.clear()
        self.main_stack.setCurrentWidget(self.page_manager_dashboard)
        self.alert_panel.show()
        
    def toggle_pause(self):
        self.label_pause.setVisible(not self.label_pause.isVisible())
        
    def add_test_alert(self):
        alert = AlertMessage("분류 공정에 문제가 발생했습니다!")
        self.alert_layout.addWidget(alert)
        
        # Auto-scroll to bottom
        scrollbar = self.alert_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
