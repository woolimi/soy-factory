"""
workers 테이블 등록·조회.
"""
from db.connection import get_connection


def create_worker(admin_id: int, name: str, card_uid: str) -> None:
    """workers 테이블에 작업자 등록. card_uid 중복 시 pymysql.IntegrityError 발생."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO `workers` (`admin_id`, `name`, `card_uid`) VALUES (%s, %s, %s)",
                (admin_id, name.strip(), card_uid.strip()),
            )
