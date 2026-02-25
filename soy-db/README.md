# SoyDB (MySQL)

제품·주소·출입·분류 등 전체 데이터 저장용 MySQL입니다.

## 실행

```bash
docker compose up -d
```

중지: `docker compose down`

## Adminer (스키마·데이터 조회)

`docker compose up -d` 후 **Adminer**가 http://localhost:8080 에서 실행됩니다. 접속하면 **soydb**로 자동 로그인됩니다.

- 이미지: `msav/adminer-autologin` (환경변수로 서버/계정/DB 지정)
- 로컬/내부용으로만 사용할 것. 외부 노출 시 보안 설정 권장.

## 접속 정보 (기본값)

- 호스트: `localhost`
- 포트: `3333`
- DB: `soydb`
- 사용자: `soy` / 비밀번호: `soy`
- root 비밀번호: `soyroot`

### 스키마·마이그레이션 (Alembic)

스키마는 **SoyServer** 쪽 **Alembic**으로 관리합니다. 마이그레이션 파일은 `soy-server/alembic/`에 있습니다.

```bash
# soy-server 디렉터리에서 실행 (MySQL 기동 후)
cd soy-server
export MYSQL_HOST=localhost MYSQL_PORT=3333 MYSQL_USER=soy MYSQL_PASSWORD=soy MYSQL_DATABASE=soydb
uv run alembic upgrade head       # 최신까지 적용
uv run alembic downgrade -1       # 직전 리비전으로 롤백
uv run alembic revision -m "설명" # 새 리비전 생성
```

DB URL을 한 번에 쓰려면 `SOY_DATABASE_URL=mysql+pymysql://soy:soy@localhost:3333/soydb` 로 설정하면 됩니다.
