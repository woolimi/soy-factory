"""
관리자 비밀번호 검증. DB의 admin 테이블 사용.
"""
import bcrypt
from sqlalchemy import text

from app.database import get_engine

BCRYPT_MAX_BYTES = 72


def _password_bytes(plain: str) -> bytes:
    return plain.encode("utf-8")[:BCRYPT_MAX_BYTES]


def verify_admin_password(plain: str) -> bool:
    """DB 첫 번째 admin의 password_hash와 일치하면 True."""
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT password_hash FROM admin ORDER BY admin_id LIMIT 1")
        ).fetchone()
    if not row:
        return False
    stored = row[0]
    if not stored:
        return False
    try:
        return bcrypt.checkpw(_password_bytes(plain), stored.encode("ascii"))
    except Exception:
        return False
