"""작업자 화면 — 잠금 화면으로 돌아가기."""


def setup_worker_screen(window, stacked) -> None:
    """작업자 화면(page_worker) 위젯 연결: 뒤로가기 → 잠금 화면."""
    def back_to_lock():
        stacked.setCurrentIndex(0)

    window.page_worker.backButton.clicked.connect(back_to_lock)
