"""잠금 화면 — 작업자 입장 버튼, 관리자 모드(비밀번호) 진입."""
import os

from PyQt6 import uic
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QDialog

from qfluentwidgets import MessageBox

from api.client import admin_login, set_auth_token
from icons import admin_icon


def setup_lock_screen(window, stacked, ui_dir: str) -> None:
    """잠금 화면(page_lock) 위젯 연결: 입장 버튼, 관리자 모드 버튼."""
    lock = window.page_lock
    lock.adminModeButton.setIcon(admin_icon())

    def go_to_worker():
        stacked.setCurrentIndex(1)

    lock.touchToEnterButton.clicked.connect(go_to_worker)

    def on_admin_mode_clicked():
        dialog = QDialog()
        uic.loadUi(os.path.join(ui_dir, "password_dialog.ui"), dialog)
        dialog.setWindowTitle("관리자 모드")
        dialog.lineEdit_password.clear()

        def try_accept():
            QGuiApplication.inputMethod().commit()
            password = dialog.lineEdit_password.text().strip()
            try:
                token = admin_login(password)
                set_auth_token(token)
                dialog.accept()
                stacked.setCurrentIndex(2)
            except (RuntimeError, TimeoutError, OSError, ConnectionError) as e:
                msg = str(e) if str(e) else "비밀번호가 올바르지 않거나 서버에 연결할 수 없습니다."
                if "비밀번호" in msg or "올바르지" in msg:
                    msg = "비밀번호가 올바르지 않습니다."
                box = MessageBox("관리자 모드", msg, dialog)
                box.cancelButton.hide()
                box.yesButton.setText("확인")
                box.exec()
                dialog.lineEdit_password.selectAll()
                dialog.lineEdit_password.setFocus()

        dialog.button_ok.clicked.connect(try_accept)
        dialog.button_cancel.clicked.connect(dialog.reject)
        dialog.lineEdit_password.returnPressed.connect(try_accept)
        dialog.exec()

    lock.adminModeButton.clicked.connect(on_admin_mode_clicked)
