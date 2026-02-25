"""
관리자 비밀번호 검증·최초 등록. DB의 admin 테이블 사용.
"""
import bcrypt
from sqlalchemy import text

from app.database import get_engine

BCRYPT_MAX_BYTES = 72


def _password_bytes(plain: str) -> bytes:
    return plain.encode("utf-8")[:BCRYPT_MAX_BYTES]


def create_first_admin(plain_password: str) -> None:
    """admin 테이블이 비어 있을 때만 첫 관리자 등록. 이미 있으면 ValueError."""
    engine = get_engine()
    with engine.connect() as conn:
        n = conn.execute(text("SELECT COUNT(*) FROM admin")).scalar()
        if n and n > 0:
            raise ValueError("이미 관리자가 등록되어 있습니다.")
    hashed = bcrypt.hashpw(
        _password_bytes(plain_password.strip()),
        bcrypt.gensalt(),
    ).decode("ascii")
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO admin (password_hash) VALUES (:h)"),
            {"h": hashed},
        )


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
