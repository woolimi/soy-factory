"""
SoyAdmin 고정 테마 (다크/라이트 감지 없이 항상 동일한 UI).
앱 전체에 적용하여 시스템 테마와 무관하게 일관된 look & feel 유지.
"""

# 색상 팔레트 (단일 고정 테마)
BG_MAIN = "#1a1a2e"
BG_SECONDARY = "#16213e"
BG_TERTIARY = "#0f0f1a"
BORDER = "#0f3460"
TEXT_PRIMARY = "#eaeaea"
TEXT_SECONDARY = "#a0a0a0"
ACCENT = "#0f3460"

# 잠금 화면 전용 — 간장 공장 느낌 (진한 갈색·앰버)
LOCK_BG = "#1a1510"
LOCK_BG_CARD = "#252018"
LOCK_AMBER = "#c9a227"
LOCK_AMBER_SOFT = "#a68b3c"
LOCK_CREAM = "#f0ebe0"
LOCK_CREAM_MUTED = "#b8ad9a"
LOCK_BORDER = "#3d3428"

GLOBAL_STYLESHEET = f"""
QWidget {{
  background-color: {BG_MAIN};
  color: {TEXT_PRIMARY};
}}
QMainWindow {{
  background-color: {BG_MAIN};
}}
QDialog {{
  background-color: {BG_MAIN};
}}
QPushButton {{
  background-color: {BG_SECONDARY};
  color: {TEXT_SECONDARY};
  border: 1px solid {BORDER};
  padding: 8px 12px;
  min-height: 20px;
}}
QPushButton:hover {{
  background-color: {BORDER};
  color: {TEXT_PRIMARY};
}}
QPushButton:pressed {{
  background-color: {BORDER};
}}
QPushButton#touchToEnterButton {{
  background-color: transparent;
  border: none;
  color: {TEXT_PRIMARY};
  font-size: 24px;
}}
QPushButton#touchToEnterButton:hover {{
  background-color: transparent;
  color: {TEXT_PRIMARY};
}}
QLabel {{
  color: {TEXT_PRIMARY};
}}
QLineEdit {{
  background-color: {BG_SECONDARY};
  color: {TEXT_PRIMARY};
  border: 1px solid {BORDER};
  padding: 8px;
  selection-background-color: {BORDER};
}}
QMenuBar {{
  background-color: {BG_MAIN};
  color: {TEXT_PRIMARY};
}}
QStatusBar {{
  background-color: {BG_MAIN};
  color: {TEXT_SECONDARY};
}}
QMessageBox {{
  background-color: {BG_MAIN};
}}

/* 잠금 화면 — 간장 공장 테마 */
QWidget#LockScreen {{
  background-color: {LOCK_BG};
}}
QWidget#LockScreen QLabel#label_lockTitle {{
  color: {LOCK_AMBER};
  font-size: 28px;
  font-weight: bold;
  letter-spacing: 1px;
}}
QWidget#LockScreen QLabel#label_lockSubtitle {{
  color: {LOCK_CREAM_MUTED};
  font-size: 13px;
}}
QWidget#LockScreen QPushButton#touchToEnterButton {{
  background-color: {LOCK_BG_CARD};
  color: {LOCK_CREAM};
  border: 2px solid {LOCK_BORDER};
  border-radius: 12px;
  font-size: 22px;
  padding: 24px;
}}
QWidget#LockScreen QPushButton#touchToEnterButton:hover {{
  background-color: {LOCK_BORDER};
  color: {LOCK_AMBER_SOFT};
  border-color: {LOCK_AMBER_SOFT};
}}
QWidget#LockScreen QLabel#label_touchHint {{
  color: {LOCK_CREAM_MUTED};
  font-size: 12px;
}}
QWidget#LockScreen QPushButton#adminModeButton {{
  background-color: {LOCK_BG_CARD};
  color: {LOCK_CREAM_MUTED};
  border: 1px solid {LOCK_BORDER};
}}
QWidget#LockScreen QPushButton#adminModeButton:hover {{
  background-color: {LOCK_BORDER};
  color: {LOCK_AMBER};
}}
"""
