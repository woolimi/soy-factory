"""최초 관리자 등록 — admin 테이블이 비어 있으면 비밀번호 등록 팝업."""
import os

from PyQt6 import uic
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QDialog, QWidget

from qfluentwidgets import MessageBox

from db import count_admins, create_admin, hash_password


def ensure_admin_registered(ui_dir: str, parent: QWidget | None = None) -> bool:
    """
    admin 테이블이 비어 있으면 최초 설정(비밀번호 등록) 팝업을 띄움.
    등록 성공 또는 이미 admin이 있으면 True, DB 오류 등으로 실패 시 False.
    """
    n = count_admins()
    if n < 0:
        w = MessageBox(
            "DB 연결 실패",
            "데이터베이스에 연결할 수 없습니다.\n"
            "MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE\n"
            "또는 SOY_DATABASE_URL 환경변수를 확인하세요.",
            parent,
        )
        w.cancelButton.hide()
        w.yesButton.setText("확인")
        w.exec()
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
            QGuiApplication.inputMethod().commit()
            pw = dialog.lineEdit_password.text().strip()
            cf = dialog.lineEdit_confirm.text().strip()
            if not pw:
                box = MessageBox("입력 오류", "비밀번호를 입력하세요.", dialog)
                box.cancelButton.hide()
                box.yesButton.setText("확인")
                box.exec()
                dialog.lineEdit_password.setFocus()
                return
            if len(pw) < 4:
                box = MessageBox("입력 오류", "비밀번호는 4자 이상으로 설정하세요.", dialog)
                box.cancelButton.hide()
                box.yesButton.setText("확인")
                box.exec()
                dialog.lineEdit_password.setFocus()
                return
            if pw != cf:
                box = MessageBox("입력 오류", "비밀번호가 일치하지 않습니다.", dialog)
                box.cancelButton.hide()
                box.yesButton.setText("확인")
                box.exec()
                dialog.lineEdit_confirm.selectAll()
                dialog.lineEdit_confirm.setFocus()
                return
            try:
                create_admin(hash_password(pw))
                box = MessageBox("등록 완료", "관리자 비밀번호가 등록되었습니다.", dialog)
                box.cancelButton.hide()
                box.yesButton.setText("확인")
                box.exec()
                dialog.accept()
            except Exception as e:
                box = MessageBox("등록 실패", f"DB 등록 중 오류가 발생했습니다.\n{e!s}", dialog)
                box.cancelButton.hide()
                box.yesButton.setText("확인")
                box.exec()

        dialog.button_ok.clicked.connect(try_register)
        dialog.button_cancel.hide()
        dialog.button_cancel.clicked.connect(dialog.reject)
        dialog.lineEdit_confirm.returnPressed.connect(try_register)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return False
        break
    return True
