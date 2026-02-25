"""관리자 화면 — 사이드바 메뉴, 작업자 관리(목록·CRUD). soy-server TCP 연동."""
import os

from PyQt6 import uic
from PyQt6.QtCore import QObject, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QDialog, QTableWidgetItem

from qfluentwidgets import MessageBox

from api import (
    WorkerCreateConflict,
    WorkerNotFound,
    create_worker as api_create_worker,
    delete_worker as api_delete_worker,
    get_first_admin_id,
    list_workers,
    update_worker as api_update_worker,
)
from api.client import admin_logout, set_card_read_callback
from serial_rfid import SerialRFIDReader, get_register_serial_port

_USE_SERVER_RFID = os.environ.get("SOY_USE_SERVER_RFID", "1").strip().lower() not in ("0", "false", "no")


class _CardReadBridge(QObject):
    """서버 TCP reader 스레드 → 메인 스레드로 UID 전달 (시그널은 스레드 안전)."""
    card_uid_received = pyqtSignal(str)


def _open_worker_info_dialog(
    parent,
    ui_dir: str,
    worker_id: int,
    name: str,
    card_uid: str,
    note: str,
    refresh_table_callback,
) -> None:
    """작업자 정보 팝업. 수정/삭제 시 API 호출 후 테이블 갱신."""
    dialog = QDialog(parent)
    uic.loadUi(os.path.join(ui_dir, "worker_info_dialog.ui"), dialog)
    dialog._worker_id = worker_id
    dialog._refresh = refresh_table_callback

    def set_labels(n: str, u: str, no: str):
        dialog.label_name_value.setText(n or "—")
        dialog.label_uid_value.setText(u or "—")
        dialog.label_note_value.setText(no or "—")

    set_labels(name, card_uid, note)

    def do_edit():
        edit_d = QDialog(parent)
        uic.loadUi(os.path.join(ui_dir, "worker_edit_dialog.ui"), edit_d)
        edit_d.nameEdit.setText(name)
        edit_d.cardUidEdit.setText(card_uid)
        edit_d.setWindowTitle("작업자 수정")

        def on_edit_ok():
            QGuiApplication.inputMethod().commit()
            new_name = edit_d.nameEdit.text().strip()
            new_uid = edit_d.cardUidEdit.text().strip()
            if not new_name:
                box = MessageBox("입력 오류", "이름을 입력하세요.", edit_d)
                box.cancelButton.hide()
                box.yesButton.setText("확인")
                box.exec()
                return
            if not new_uid:
                box = MessageBox("입력 오류", "카드 UID를 입력하세요.", edit_d)
                box.cancelButton.hide()
                box.yesButton.setText("확인")
                box.exec()
                return
            try:
                api_update_worker(worker_id, name=new_name, card_uid=new_uid)
            except WorkerCreateConflict as e:
                box = MessageBox("수정 실패", e.detail, edit_d)
                box.cancelButton.hide()
                box.yesButton.setText("확인")
                box.exec()
                return
            except WorkerNotFound:
                box = MessageBox("수정 실패", "작업자를 찾을 수 없습니다.", edit_d)
                box.cancelButton.hide()
                box.yesButton.setText("확인")
                box.exec()
                edit_d.reject()
                return
            except (TimeoutError, RuntimeError, OSError, ConnectionError) as e:
                box = MessageBox("수정 실패", f"서버 통신 오류:\n{e!s}", edit_d)
                box.cancelButton.hide()
                box.yesButton.setText("확인")
                box.exec()
                return
            refresh_table_callback()
            set_labels(new_name, new_uid, note)
            edit_d.accept()

        edit_d.button_ok.clicked.connect(on_edit_ok)
        edit_d.button_cancel.clicked.connect(edit_d.reject)
        edit_d.nameEdit.returnPressed.connect(on_edit_ok)
        edit_d.exec()

    def do_delete():
        box = MessageBox(
            "삭제 확인",
            "이 작업자를 삭제하시겠습니까?",
            dialog,
        )
        if box.exec() != 1:  # Yes
            return
        try:
            api_delete_worker(worker_id)
        except WorkerNotFound:
            box2 = MessageBox("삭제 실패", "작업자를 찾을 수 없습니다.", dialog)
            box2.cancelButton.hide()
            box2.yesButton.setText("확인")
            box2.exec()
            return
        except (TimeoutError, RuntimeError, OSError, ConnectionError) as e:
            box2 = MessageBox("삭제 실패", f"서버 통신 오류:\n{e!s}", dialog)
            box2.cancelButton.hide()
            box2.yesButton.setText("확인")
            box2.exec()
            return
        refresh_table_callback()
        dialog.accept()

    dialog.button_edit.clicked.connect(do_edit)
    dialog.button_delete.clicked.connect(do_delete)
    dialog.button_close.clicked.connect(dialog.reject)
    dialog.exec()


def setup_admin_screen(window, stacked, ui_dir: str) -> None:
    """관리자 화면: 사이드바, 작업자 관리(목록·추가·정보 팝업에서 수정/삭제)."""
    admin = window.page_admin
    admin.workerTable.setHorizontalHeaderLabels(["이름", "카드 UID", "비고"])

    def refresh_workers():
        try:
            workers = list_workers()
        except (TimeoutError, RuntimeError, OSError, ConnectionError) as e:
            return  # 조용히 실패하거나 상태바에 표시 가능
        admin.workerTable.setRowCount(0)
        for w in workers:
            row = admin.workerTable.rowCount()
            admin.workerTable.insertRow(row)
            item0 = QTableWidgetItem(w.get("name", ""))
            item0.setData(Qt.ItemDataRole.UserRole, w.get("worker_id"))
            admin.workerTable.setItem(row, 0, item0)
            admin.workerTable.setItem(row, 1, QTableWidgetItem(w.get("card_uid", "")))
            admin.workerTable.setItem(row, 2, QTableWidgetItem(""))

    def on_worker_cell_clicked(row: int, _column: int):
        if row < 0:
            return
        item0 = admin.workerTable.item(row, 0)
        worker_id = item0.data(Qt.ItemDataRole.UserRole) if item0 else None
        if worker_id is None:
            return
        name = item0.text() if item0 else ""
        uid = ""
        note = ""
        if admin.workerTable.item(row, 1):
            uid = admin.workerTable.item(row, 1).text()
        if admin.workerTable.item(row, 2):
            note = admin.workerTable.item(row, 2).text()
        _open_worker_info_dialog(
            window, ui_dir, worker_id, name, uid, note, refresh_workers
        )

    admin.workerTable.cellClicked.connect(on_worker_cell_clicked)

    def on_current_changed(index: int):
        if stacked.widget(index) == admin:
            refresh_workers()

    stacked.currentChanged.connect(on_current_changed)

    def back_to_lock():
        admin_logout()
        stacked.setCurrentIndex(0)

    admin.backButton.clicked.connect(back_to_lock)

    def on_add_worker_clicked():
        dialog = QDialog(window)
        uic.loadUi(os.path.join(ui_dir, "worker_registration_dialog.ui"), dialog)
        dialog._scanned_uid = None
        rfid_reader: SerialRFIDReader | None = None

        def on_rfid_ui(uid: str) -> None:
            """메인 스레드에서 UI 갱신 (TCP 콜백 또는 시리얼 시그널에서 호출)."""
            dialog._scanned_uid = uid or dialog._scanned_uid
            display_uid = (uid or dialog._scanned_uid) or "—"
            dialog.statusLabel.setText(
                f"카드 인식 완료 (UID: {display_uid}). 작업자 이름을 입력하세요."
            )
            dialog.workerNameEdit.setEnabled(True)
            dialog.button_ok.setEnabled(True)
            QTimer.singleShot(0, dialog.workerNameEdit.setFocus)

        if _USE_SERVER_RFID:
            # 서버 TCP 콜백은 reader 스레드에서 호출됨 → 시그널로 메인 스레드에 전달해야 UI 갱신됨
            bridge = _CardReadBridge()
            bridge.card_uid_received.connect(on_rfid_ui)

            def on_card_read_from_server(uid: str) -> None:
                bridge.card_uid_received.emit(uid)

            set_card_read_callback(on_card_read_from_server)
            try:
                get_first_admin_id()
                dialog.statusLabel.setText("서버에 연결됨. RFID 카드를 찍어주세요.")
            except (TimeoutError, RuntimeError, OSError, ConnectionError):
                dialog.statusLabel.setText(
                    "서버에 연결할 수 없습니다. soy-server가 실행 중인지 확인하세요."
                )
        else:
            port = get_register_serial_port()
            if port:
                rfid_reader = SerialRFIDReader(port, parent=dialog)
                rfid_reader.card_uid_received.connect(on_rfid_ui)

                def on_error(msg: str):
                    box = MessageBox("시리얼 오류", msg, dialog)
                    box.cancelButton.hide()
                    box.yesButton.setText("확인")
                    box.exec()

                rfid_reader.error_occurred.connect(on_error)
                rfid_reader.start()
                dialog.statusLabel.setText(f"RFID 카드를 찍어주세요. (시리얼: {port})")
            else:
                dialog.statusLabel.setText(
                    "시리얼 포트를 사용할 수 없습니다. Register Controller를 연결하세요."
                )

        def try_accept():
            QGuiApplication.inputMethod().commit()
            name = dialog.workerNameEdit.text().strip()
            if not name:
                box = MessageBox("입력 오류", "작업자 이름을 입력하세요.", dialog)
                box.cancelButton.hide()
                box.yesButton.setText("확인")
                box.exec()
                dialog.workerNameEdit.setFocus()
                return
            uid = getattr(dialog, "_scanned_uid", None)
            if not uid or uid.strip() == "":
                box = MessageBox("입력 오류", "RFID 카드를 먼저 찍어주세요.", dialog)
                box.cancelButton.hide()
                box.yesButton.setText("확인")
                box.exec()
                return
            admin_id = get_first_admin_id()
            if admin_id is None:
                box = MessageBox("등록 실패", "관리자가 등록되지 않았습니다.", dialog)
                box.cancelButton.hide()
                box.yesButton.setText("확인")
                box.exec()
                return
            try:
                api_create_worker(admin_id, name, uid)
            except WorkerCreateConflict as e:
                box = MessageBox("등록 실패", e.detail, dialog)
                box.cancelButton.hide()
                box.yesButton.setText("확인")
                box.exec()
                return
            except (TimeoutError, RuntimeError, OSError, ConnectionError) as e:
                box = MessageBox(
                    "등록 실패",
                    f"서버 통신 오류. soy-server가 실행 중인지 확인하세요.\n{e!s}",
                    dialog,
                )
                box.cancelButton.hide()
                box.yesButton.setText("확인")
                box.exec()
                return
            box = MessageBox(
                "등록 완료",
                f"작업자 '{name}' (카드 UID: {uid}) 정보가 등록되었습니다.",
                dialog,
            )
            box.cancelButton.hide()
            box.yesButton.setText("확인")
            box.exec()
            refresh_workers()
            dialog.accept()

        def on_finished():
            if _USE_SERVER_RFID:
                set_card_read_callback(None)
            elif rfid_reader and rfid_reader.isRunning():
                rfid_reader.stop()
                rfid_reader.wait(2000)

        dialog.button_ok.clicked.connect(try_accept)
        dialog.button_cancel.clicked.connect(dialog.reject)
        dialog.workerNameEdit.returnPressed.connect(try_accept)
        dialog.finished.connect(on_finished)
        dialog.exec()

    admin.addWorkerButton.clicked.connect(on_add_worker_clicked)
