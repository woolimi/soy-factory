"""
SoyAdmin DB 연동 — admin 테이블 조회·등록·비밀번호 검증.
연결 정보는 환경변수 (SOY_DATABASE_URL 또는 MYSQL_*).
"""
import os
from contextlib import contextmanager
from typing import Generator

import bcrypt
import pymysql

# bcrypt 최대 72바이트. 초과 분은 잘라서 해시/검증 (에러 방지).
BCRYPT_MAX_BYTES = 72


def _get_connection_params() -> dict:
    from urllib.parse import unquote

    url = os.environ.get("SOY_DATABASE_URL")
    if url and url.startswith("mysql"):
        from urllib.parse import urlparse
        parsed = urlparse(url)
        db_path = (parsed.path or "/soydb").lstrip("/")
        return {
            "host": parsed.hostname or "127.0.0.1",
            "port": parsed.port if parsed.port is not None else 3306,
            "user": unquote(parsed.username) if parsed.username else "soy",
            "password": unquote(parsed.password) if parsed.password else "soy",
            "database": db_path or "soydb",
            "charset": "utf8mb4",
        }
    return {
        "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.environ.get("MYSQL_PORT", "3333")),
        "user": os.environ.get("MYSQL_USER", "soy"),
        "password": os.environ.get("MYSQL_PASSWORD", "soy"),
        "database": os.environ.get("MYSQL_DATABASE", "soydb"),
        "charset": "utf8mb4",
    }


@contextmanager
def get_connection() -> Generator[pymysql.Connection, None, None]:
    params = _get_connection_params()
    conn = pymysql.connect(**params)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def count_admins() -> int:
    """admin 테이블 레코드 수. 연결 실패 시 -1."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM `admin`")
                return int(cur.fetchone()[0])
    except Exception:
        return -1


def create_admin(password_hash: str) -> None:
    """admin 한 명 등록 (password_hash는 bcrypt 등 이미 해시된 값)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO `admin` (`password_hash`) VALUES (%s)",
                (password_hash,),
            )


def get_first_admin_password_hash() -> str | None:
    """첫 번째 admin의 password_hash. 없으면 None."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT `password_hash` FROM `admin` LIMIT 1")
                row = cur.fetchone()
                return row[0] if row else None
    except Exception:
        return None


def _password_bytes(plain: str) -> bytes:
    """bcrypt 72바이트 제한 적용."""
    return plain.encode("utf-8")[:BCRYPT_MAX_BYTES]


def verify_admin_password(plain: str) -> bool:
    """DB에 저장된 admin 비밀번호와 일치하면 True."""
    h = get_first_admin_password_hash()
    if not h:
        return False
    try:
        return bcrypt.checkpw(_password_bytes(plain), h.encode("ascii"))
    except Exception:
        return False


def hash_password(plain: str) -> str:
    """비밀번호를 bcrypt 해시 문자열로 반환 (72바이트 초과 분 절단)."""
    raw = _password_bytes(plain)
    return bcrypt.hashpw(raw, bcrypt.gensalt()).decode("ascii")
