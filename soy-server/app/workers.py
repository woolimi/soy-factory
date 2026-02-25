"""
Worker CRUD — DB 로직만. HTTP/TCP 핸들러에서 공통 사용.
"""
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine

from app.database import get_engine


class WorkerNotFound(Exception):
    pass


class WorkerCreateConflict(Exception):
    def __init__(self, detail: str = ""):
        self.detail = detail
        super().__init__(detail)


def _row_to_worker(row) -> dict:
    return {
        "worker_id": row[0],
        "admin_id": row[1],
        "name": row[2],
        "card_uid": row[3],
        "created_at": row[4].isoformat() if hasattr(row[4], "isoformat") else str(row[4]),
    }


def count_admins(engine: Engine | None = None) -> int:
    """admin 테이블 레코드 수. 연결 실패 시 예외."""
    eng = engine or get_engine()
    with eng.connect() as conn:
        return int(conn.execute(text("SELECT COUNT(*) FROM admin")).scalar() or 0)


def get_first_admin_id(engine: Engine | None = None) -> int | None:
    eng = engine or get_engine()
    with eng.connect() as conn:
        row = conn.execute(
            text("SELECT admin_id FROM admin ORDER BY admin_id LIMIT 1")
        ).fetchone()
        return int(row[0]) if row else None


def list_workers(engine: Engine | None = None) -> list[dict]:
    eng = engine or get_engine()
    with eng.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT worker_id, admin_id, name, card_uid, created_at FROM workers ORDER BY worker_id"
            )
        ).fetchall()
        return [_row_to_worker(r) for r in rows]


def create_worker(
    admin_id: int,
    name: str,
    card_uid: str,
    engine: Engine | None = None,
) -> dict:
    eng = engine or get_engine()
    name = name.strip()
    card_uid = card_uid.strip()
    with eng.begin() as conn:
        try:
            conn.execute(
                text(
                    "INSERT INTO workers (admin_id, name, card_uid) VALUES (:aid, :name, :uid)"
                ),
                {"aid": admin_id, "name": name, "uid": card_uid},
            )
        except IntegrityError as e:
            orig = getattr(e, "orig", e)
            if "Duplicate" in str(orig) or "card_uid" in str(orig):
                raise WorkerCreateConflict("이 카드 UID는 이미 등록된 작업자가 있습니다.") from e
            raise
        row = conn.execute(
            text(
                "SELECT worker_id, admin_id, name, card_uid, created_at FROM workers WHERE card_uid = :uid ORDER BY worker_id DESC LIMIT 1"
            ),
            {"uid": card_uid},
        ).fetchone()
    if not row:
        raise RuntimeError("Insert succeeded but fetch failed")
    return _row_to_worker(row)


def update_worker(
    worker_id: int,
    *,
    name: str | None = None,
    card_uid: str | None = None,
    engine: Engine | None = None,
) -> dict:
    eng = engine or get_engine()
    updates = []
    params: dict = {"wid": worker_id}
    if name is not None:
        updates.append("name = :name")
        params["name"] = name.strip()
    if card_uid is not None:
        updates.append("card_uid = :uid")
        params["uid"] = card_uid.strip()
    if not updates:
        with eng.connect() as conn:
            row = conn.execute(
                text(
                    "SELECT worker_id, admin_id, name, card_uid, created_at FROM workers WHERE worker_id = :wid"
                ),
                {"wid": worker_id},
            ).fetchone()
            if not row:
                raise WorkerNotFound()
            return _row_to_worker(row)
    with eng.begin() as conn:
        try:
            conn.execute(
                text(f"UPDATE workers SET {', '.join(updates)} WHERE worker_id = :wid"),
                params,
            )
        except IntegrityError as e:
            orig = getattr(e, "orig", e)
            if "Duplicate" in str(orig) or "card_uid" in str(orig):
                raise WorkerCreateConflict(
                    "이 카드 UID는 이미 다른 작업자가 사용 중입니다."
                ) from e
            raise
        row = conn.execute(
            text(
                "SELECT worker_id, admin_id, name, card_uid, created_at FROM workers WHERE worker_id = :wid"
            ),
            {"wid": worker_id},
        ).fetchone()
    if not row:
        raise WorkerNotFound()
    return _row_to_worker(row)


def delete_worker(worker_id: int, engine: Engine | None = None) -> None:
    eng = engine or get_engine()
    with eng.begin() as conn:
        r = conn.execute(
            text("DELETE FROM workers WHERE worker_id = :wid"),
            {"wid": worker_id},
        )
        if r.rowcount == 0:
            raise WorkerNotFound()
