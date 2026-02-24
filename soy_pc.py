#!/usr/bin/env python3
"""SoyAdmin(soy-pc) PyQt 앱 실행. 루트에서: uv run python run_soy_pc.py"""
import os
import subprocess
import sys


def main() -> int:
    root = os.path.dirname(os.path.abspath(__file__))
    main_py = os.path.join(root, "soy-pc", "main.py")
    return subprocess.run([sys.executable, main_py], cwd=root).returncode


if __name__ == "__main__":
    sys.exit(main())
