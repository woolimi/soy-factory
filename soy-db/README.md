# SoyDB (MySQL)

제품·주소·출입·분류 등 전체 데이터 저장용 MySQL입니다.

## 실행

```bash
docker compose up -d
```

중지: `docker compose down`

## 접속 정보 (기본값)

- 호스트: `localhost`
- 포트: `3306`
- DB: `soydb`
- 사용자: `soy` / 비밀번호: `soy`
- root 비밀번호: `soyroot`

스키마·테이블은 SoyServer 쪽 Alembic 마이그레이션으로 관리합니다.
