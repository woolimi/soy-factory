"""
admin 테이블 조회·등록·비밀번호 검증.
"""
import bcrypt

from db.connection import get_connection

BCRYPT_MAX_BYTES = 72


def _password_bytes(plain: str) -> bytes:
    return plain.encode("utf-8")[:BCRYPT_MAX_BYTES]


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


def get_first_admin_id() -> int | None:
    """첫 번째 admin의 admin_id. 없으면 None."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT `admin_id` FROM `admin` LIMIT 1")
                row = cur.fetchone()
                return int(row[0]) if row else None
    except Exception:
        return None


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
