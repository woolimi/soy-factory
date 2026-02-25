"""
DB 연결. 환경변수 SOY_DATABASE_URL 또는 MYSQL_* 사용.
"""
import os
from contextlib import contextmanager
from typing import Generator

import pymysql


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
