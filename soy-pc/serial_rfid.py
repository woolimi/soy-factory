"""
Register Controller(Arduino + RFID) 시리얼 수신.
NDJSON 프로토콜 파싱 (docs/soy-kit-protocol.md): 한 줄에 하나의 JSON.
type=="card_read" 시 uid 시그널 발생.
"""
import json
import os
from typing import Any, Optional

from PyQt6.QtCore import QThread, pyqtSignal

# pyserial은 run 시점에 import (의존성은 pyproject.toml에 있음)
try:
    import serial
    import serial.tools.list_ports
except ImportError:
    serial = None  # type: ignore[assignment]
    list_ports = None  # type: ignore[assignment]


# register_controller.ino 와 동일
DEFAULT_BAUD = 9600

# 프로토콜 (Serial/TCP 공통)
SOURCE_REGISTER_CONTROLLER = "register_controller"


def parse_kit_message(line: str) -> Optional[dict[str, Any]]:
    """
    NDJSON 한 줄을 파싱. type, source 가 있으면 메시지 dict 반환, 아니면 None.
    """
    line = line.strip()
    if not line:
        return None
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        return None
    if not isinstance(obj, dict):
        return None
    if "type" not in obj or "source" not in obj:
        return None
    return obj


def get_register_serial_port() -> Optional[str]:
    """
    환경변수 SOY_REGISTER_SERIAL_PORT 가 있으면 해당 포트 사용.
    없으면 목록에서 첫 번째 사용 가능 포트 반환 (없으면 None).
    """
    env_port = os.environ.get("SOY_REGISTER_SERIAL_PORT", "").strip()
    if env_port:
        return env_port
    if serial is None:
        return None
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        return None
    # Arduino/USB 직렬 장치 우선 (이름에 USB, ACM, usbmodem 등 포함)
    for p in ports:
        desc = (p.description or "").upper()
        name = (p.device or "").upper()
        if "ARDUINO" in desc or "USB" in desc or "USB" in name or "ACM" in name or "USBMODEM" in name:
            return p.device
    return ports[0].device


class SerialRFIDReader(QThread):
    """
    시리얼로부터 NDJSON 한 줄씩 읽어, type=="card_read" 이면 card_uid_received(str) 시그널 발생.
    프로토콜: docs/soy-kit-protocol.md
    """
    card_uid_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, port: str, baud: int = DEFAULT_BAUD, parent=None):
        super().__init__(parent)
        self.port = port
        self.baud = baud
        self._running = True

    def run(self) -> None:
        if serial is None:
            self.error_occurred.emit("pyserial이 설치되지 않았습니다.")
            return
        try:
            ser = serial.Serial(self.port, self.baud, timeout=0.3)
        except Exception as e:
            msg = f"{e!s}"
            if getattr(e, "errno", None) == 16 or "Resource busy" in msg or "Errno 16" in msg:
                self.error_occurred.emit(
                    f"시리얼 포트가 다른 프로그램에서 사용 중입니다 ({self.port}).\n"
                    "Arduino IDE 시리얼 모니터를 닫은 뒤 다시 시도하세요."
                )
            else:
                self.error_occurred.emit(f"시리얼 열기 실패 ({self.port}): {e!s}")
            return
        try:
            while self._running:
                try:
                    line = ser.readline().decode("utf-8", errors="ignore").strip()
                except Exception:
                    continue
                msg = parse_kit_message(line)
                if not msg or msg.get("type") != "card_read":
                    continue
                uid = msg.get("uid")
                if isinstance(uid, str) and uid:
                    self.card_uid_received.emit(uid)
        finally:
            try:
                ser.close()
            except Exception:
                pass

    def stop(self) -> None:
        self._running = False
