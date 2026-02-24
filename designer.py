#!/usr/bin/env python3
"""Qt Designer 실행. Qt가 설치되어 있고 designer가 PATH에 있어야 합니다.
   macOS: brew install qt → /opt/homebrew/opt/qt/bin/designer
   Linux: 보통 qt6-tools-base 또는 qt5-tools 등에서 designer 제공."""
import os
import shutil
import subprocess
import sys


def main() -> int:
    designer = shutil.which("designer")
    if not designer:
        # macOS Homebrew Qt
        for path in (
            "/opt/homebrew/opt/qt/bin/designer",
            "/usr/local/opt/qt/bin/designer",
        ):
            if os.path.isfile(path):
                designer = path
                break
    if not designer:
        print("Qt Designer를 찾을 수 없습니다.", file=sys.stderr)
        print("  macOS: brew install qt", file=sys.stderr)
        print("  Linux: 패키지 관리자에서 qt6-tools-base 또는 qt5-tools 설치", file=sys.stderr)
        return 1
    root = os.path.dirname(os.path.abspath(__file__))
    ui_path = os.path.join(root, "soy-pc", "soy-pc.ui")
    return subprocess.run([designer, ui_path], cwd=root).returncode


if __name__ == "__main__":
    sys.exit(main())
