#!/bin/sh
set -e
cd /app/soy-server
echo "[entrypoint] Running DB migrations..."
alembic upgrade head
echo "[entrypoint] Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir .
