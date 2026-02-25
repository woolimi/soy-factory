# Agent 가이드 — Smart Soy Sauce Factory (스마트 간장공장)

AI 에이전트가 이 저장소에서 작업할 때 참고할 프로젝트 컨텍스트와 규칙입니다. 상세 개요·실행 방법은 [README.md](./README.md)를 참고하세요.

---

## 1. 프로젝트 요약

- **목적**: 제품 상자 QR 코드의 주소를 읽어 **국내/해외**로 자동 분류하는 스마트 간장공장 소프트웨어.
- **흐름**: 컨베이어 → ESP32CAM(QR 인식) → SoyServer(주소 해석·분류 지시) → 서보모터로 창고 분류.
- **통신**: 출입제어키트·분류키트·관리자 PC는 **중앙서버(SoyServer)** 를 통해 **SoyDB(MySQL)** 와 연동.

---

## 2. 저장소 구조 및 모듈별 가이드

| 경로 | 역할 | 스택 | 에이전트 작업 시 참고 |
|------|------|------|------------------------|
| `soy-server/` | 중앙서버 | Python 3.12, FastAPI, Alembic·SQLAlchemy | REST API·비동기·DB 연동. **Alembic은 soy-server/ 내부(soy-server/alembic/)에서 관리.** 스키마 변경 시 마이그레이션과 정합성 유지. |
| `soy-pc/` | 관리자/작업자 UI (SoyAdmin) | PyQt6 | `soy-pc.ui` + `main.py`. 루트의 `designer.py`로 UI 편집, `soy_pc.py`로 실행. SoyServer·카메라 UDP 연동. |
| `soy-db/` | DB·인프라 | MySQL, Docker | 스키마·Docker 설정. 테이블 변경은 SoyServer 쪽 마이그레이션과 맞출 것. |
| `soy-controller/` | 분류키트 | Arduino, ESP32CAM | QR 인식, 근접·서보·DC모터. **TCP**(분류 지시)·**UDP**(카메라). |
| `access-controller/` | 출입제어키트 | Arduino, ESP32, RFID | 중앙서버와 **TCP** 통신. |

**루트 주요 파일**

- `pyproject.toml`, `uv.lock` — Python 의존성 (서버·PyQt6 등). 패키지 추가 시 `uv add [패키지]`.
- `docker-compose.yml` — MySQL + SoyServer 한 번에 기동. `docker compose up -d`.
- `designer.py` — Qt Designer 실행, `soy-pc/soy-pc.ui` 열기.
- `soy_pc.py` — SoyAdmin 앱 실행 (`soy-pc/main.py` 호출).

---

## 3. 자주 쓰는 명령 (루트 기준)

```bash
uv venv && uv sync                    # 프로젝트 세팅
docker compose up -d                  # 서버·DB 기동
uv run uvicorn app.main:app --app-dir soy-server --reload   # 서버만 로컬 실행
uv run python designer.py             # Qt Designer (soy-pc.ui 편집)
uv run python soy_pc.py               # SoyAdmin 실행
cd soy-server && uv run alembic upgrade head   # DB 마이그레이션 적용
```

펌웨어(access-controller, soy-controller)는 VSCode + PlatformIO IDE로 해당 폴더를 열어 빌드·업로드.
