"""create inbound_info table (입고정보)

입고 id + 물품명 + 브랜드로 한 건 식별.
입고예정 개수(expected_quantity), 입고된 개수(received_quantity, 기본 0) 기록.
나중에 QR 코드로 입력 등 확장 예정.

Revision ID: 004
Revises: 003
Create Date: 2025-02-26

"""
from typing import Sequence, Union

from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET NAMES utf8mb4")
    op.execute("SET FOREIGN_KEY_CHECKS = 0")

    op.execute("""
        CREATE TABLE IF NOT EXISTS `inbound_info` (
            `inbound_id`         INT UNSIGNED NOT NULL COMMENT '입고 id',
            `product_name`       VARCHAR(100) NOT NULL COMMENT '물품명',
            `brand`              VARCHAR(50)  NOT NULL COMMENT '브랜드',
            `expected_quantity`  INT UNSIGNED  NOT NULL COMMENT '입고예정 개수',
            `received_quantity`  INT UNSIGNED  NOT NULL DEFAULT 0 COMMENT '입고된 개수',
            PRIMARY KEY (`inbound_id`, `product_name`, `brand`),
            KEY `idx_inbound_info_inbound_id` (`inbound_id`),
            KEY `idx_inbound_info_received_quantity` (`received_quantity`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)

    op.execute("SET FOREIGN_KEY_CHECKS = 1")


def downgrade() -> None:
    op.execute("SET FOREIGN_KEY_CHECKS = 0")
    op.execute("DROP TABLE IF EXISTS `inbound_info`")
    op.execute("SET FOREIGN_KEY_CHECKS = 1")
