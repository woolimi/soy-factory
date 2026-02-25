"""
DB 연결. 환경변수 SOY_DATABASE_URL 또는 MYSQL_* 사용 (alembic/env와 동일).
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

_env = os.environ


def _get_url() -> str:
    url = _env.get("SOY_DATABASE_URL")
    if url:
        return url
    user = _env.get("MYSQL_USER", "soy")
    password = _env.get("MYSQL_PASSWORD", "soy")
    host = _env.get("MYSQL_HOST", "127.0.0.1")
    port = _env.get("MYSQL_PORT", "3333")
    database = _env.get("MYSQL_DATABASE", "soydb")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"


_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(_get_url(), pool_pre_ping=True)
    return _engine
