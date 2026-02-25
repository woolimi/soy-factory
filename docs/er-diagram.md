# ER Diagram — Smart Soy Sauce Factory

SYSTEM_REQUIREMENTS.md 기반 DB 스키마 개념 설계.  
아래 Mermaid 코드는 GitHub/GitLab, Cursor, VS Code 등에서 렌더링 가능하다.

---

```mermaid
erDiagram
    admin {
        int admin_id PK
        string password_hash
        datetime created_at
        datetime updated_at
    }

    worker {
        int worker_id PK
        int admin_id FK
        string name
        string card_uid
        datetime created_at
    }

    access_log {
        int access_log_id PK
        int worker_id FK
        datetime checked_at
        string direction "in / out"
    }

    admin ||--o{ worker : "발급·관리 (1:N)"
    worker ||--o{ access_log : "출입 (1:N)"
```

---

## 엔티티 요약

| 엔티티 | 요구사항 | 설명 |
|--------|----------|------|
| **admin** | S-01 | 관리자(admin_id, 비밀번호 해시) |
| **worker** | S-02, S-03 | 작업자(worker_id, 발급 관리자, 이름, 카드 UID) |
| **access_log** | S-04 | 작업자별 출입 로그(시각, 출입 방향) |

나머지 테이블(입고, 분류 공정, 로그 등)은 추후 반영 예정.
