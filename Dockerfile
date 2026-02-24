# SoyServer (FastAPI) — 프로젝트 루트에서 빌드
FROM python:3.12-slim

WORKDIR /app

# 의존성만 먼저 복사해 레이어 캐시 활용
COPY pyproject.toml uv.lock ./
COPY soy-server/ ./soy-server/

# pyproject.toml 기준 의존성 설치 (패키지 구조 없이 deps만)
RUN pip install --no-cache-dir fastapi "uvicorn[standard]"

EXPOSE 8000

# DB 연결은 환경변수로 (MYSQL_HOST 등) Compose에서 주입
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "soy-server"]
