import os
import sys

from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QMainWindow,
    QMessageBox,
    QStackedLayout,
)

from db import count_admins, create_admin, hash_password, verify_admin_password
from icons import admin_icon
from theme import GLOBAL_STYLESHEET


def ensure_admin_registered(ui_dir: str, parent: QMainWindow | None = None) -> bool:
    """
    admin 테이블이 비어 있으면 최초 설정(비밀번호 등록) 팝업을 띄움.
    등록 성공 또는 이미 admin이 있으면 True, DB 오류 등으로 실패 시 False.
    """
    n = count_admins()
    if n < 0:
        QMessageBox.warning(
            parent,
            "DB 연결 실패",
            "데이터베이스에 연결할 수 없습니다.\n"
            "MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE\n"
            "또는 SOY_DATABASE_URL 환경변수를 확인하세요.",
            QMessageBox.StandardButton.Ok,
        )
        return False
    if n > 0:
        return True

    # admin 0명 → 등록 팝업
    while True:
        dialog = QDialog(parent)
        uic.loadUi(
            os.path.join(ui_dir, "admin_registration_dialog.ui"),
            dialog,
        )
        dialog.setWindowTitle("최초 설정 — 관리자 등록")

        def try_register() -> None:
            pw = dialog.lineEdit_password.text().strip()
            cf = dialog.lineEdit_confirm.text().strip()
            if not pw:
                QMessageBox.warning(
                    dialog,
                    "입력 오류",
                    "비밀번호를 입력하세요.",
                    QMessageBox.StandardButton.Ok,
                )
                dialog.lineEdit_password.setFocus()
                return
            if len(pw) < 4:
                QMessageBox.warning(
                    dialog,
                    "입력 오류",
                    "비밀번호는 4자 이상으로 설정하세요.",
                    QMessageBox.StandardButton.Ok,
                )
                dialog.lineEdit_password.setFocus()
                return
            if pw != cf:
                QMessageBox.warning(
                    dialog,
                    "입력 오류",
                    "비밀번호가 일치하지 않습니다.",
                    QMessageBox.StandardButton.Ok,
                )
                dialog.lineEdit_confirm.selectAll()
                dialog.lineEdit_confirm.setFocus()
                return
            try:
                create_admin(hash_password(pw))
                QMessageBox.information(
                    dialog,
                    "등록 완료",
                    "관리자 비밀번호가 등록되었습니다.",
                    QMessageBox.StandardButton.Ok,
                )
                dialog.accept()
            except Exception as e:
                QMessageBox.warning(
                    dialog,
                    "등록 실패",
                    f"DB 등록 중 오류가 발생했습니다.\n{e!s}",
                    QMessageBox.StandardButton.Ok,
                )

        dialog.button_ok.clicked.connect(try_register)
        dialog.button_cancel.clicked.connect(dialog.reject)
        dialog.lineEdit_confirm.returnPressed.connect(try_register)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return False
        # 등록 성공
        break
    return True


def main():
    app = QApplication(sys.argv)
    base = os.path.dirname(__file__)
    ui_dir = os.path.join(base, "ui")

    # 고정 테마 적용 (다크/라이트 감지 없이 일관된 UI)
    app.setStyleSheet(GLOBAL_STYLESHEET)

    # 메인 윈도우: 스택만 포함
    window = QMainWindow()
    uic.loadUi(os.path.join(ui_dir, "main_window.ui"), window)
    window.setWindowTitle("SoyAdmin")

    # 화면별 .ui 로드
    uic.loadUi(os.path.join(ui_dir, "lock_screen.ui"), window.page_lock)
    uic.loadUi(os.path.join(ui_dir, "worker_screen.ui"), window.page_worker)
    uic.loadUi(os.path.join(ui_dir, "admin_screen.ui"), window.page_admin)

    stacked = window.centralwidget.layout()
    if not isinstance(stacked, QStackedLayout):
        raise RuntimeError("centralwidget layout must be QStackedLayout")
    stacked.setCurrentIndex(0)  # 잠금 화면

    # admin 없으면 최초 설정 팝업 (첫 화면에서)
    if not ensure_admin_registered(ui_dir, window):
        # 사용자가 등록 다이얼로그를 취소했거나 DB 연결 실패
        pass  # 그대로 메인 창은 띄움 (재시도 가능하도록)

    # 잠금 화면 위젯 (page_lock)
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
            if verify_admin_password(dialog.lineEdit_password.text().strip()):
                dialog.accept()
                stacked.setCurrentIndex(2)
            else:
                QMessageBox.warning(
                    dialog,
                    "비밀번호 오류",
                    "비밀번호가 올바르지 않습니다.",
                    QMessageBox.StandardButton.Ok,
                )
                dialog.lineEdit_password.selectAll()
                dialog.lineEdit_password.setFocus()

        dialog.button_ok.clicked.connect(try_accept)
        dialog.button_cancel.clicked.connect(dialog.reject)
        dialog.lineEdit_password.returnPressed.connect(try_accept)
        dialog.exec()

    lock.adminModeButton.clicked.connect(on_admin_mode_clicked)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
