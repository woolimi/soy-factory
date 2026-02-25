"""create admin, worker, access_log tables

Revision ID: 001
Revises:
Create Date: 2025-02-25

"""
from typing import Sequence, Union

from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET NAMES utf8mb4")
    op.execute("SET FOREIGN_KEY_CHECKS = 0")

    op.execute("""
        CREATE TABLE IF NOT EXISTS `admin` (
            `admin_id`      INT UNSIGNED NOT NULL AUTO_INCREMENT,
            `password_hash` VARCHAR(255) NOT NULL,
            `created_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `updated_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (`admin_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS `worker` (
            `worker_id`  INT UNSIGNED NOT NULL AUTO_INCREMENT,
            `admin_id`   INT UNSIGNED NOT NULL,
            `name`       VARCHAR(100) NOT NULL,
            `card_uid`   VARCHAR(64)  NOT NULL COMMENT 'RFID 카드 UID',
            `created_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (`worker_id`),
            UNIQUE KEY `uk_worker_card_uid` (`card_uid`),
            KEY `idx_worker_admin_id` (`admin_id`),
            CONSTRAINT `fk_worker_admin` FOREIGN KEY (`admin_id`) REFERENCES `admin` (`admin_id`) ON DELETE RESTRICT ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS `access_log` (
            `access_log_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
            `worker_id`     INT UNSIGNED NOT NULL,
            `checked_at`    DATETIME     NOT NULL,
            `direction`     VARCHAR(10)  NOT NULL COMMENT 'in / out',
            PRIMARY KEY (`access_log_id`),
            KEY `idx_access_log_worker_id` (`worker_id`),
            KEY `idx_access_log_checked_at` (`checked_at`),
            CONSTRAINT `fk_access_log_worker` FOREIGN KEY (`worker_id`) REFERENCES `worker` (`worker_id`) ON DELETE RESTRICT ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)

    op.execute("SET FOREIGN_KEY_CHECKS = 1")


def downgrade() -> None:
    op.execute("SET FOREIGN_KEY_CHECKS = 0")
    op.execute("DROP TABLE IF EXISTS `access_log`")
    op.execute("DROP TABLE IF EXISTS `worker`")
    op.execute("DROP TABLE IF EXISTS `admin`")
    op.execute("SET FOREIGN_KEY_CHECKS = 1")
