-- Smart Soy Sauce Factory — admin, worker, access_log
-- ER diagram: soy-db/er-diagram.md

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- --------------------------------------
-- admin (관리자)
-- --------------------------------------
CREATE TABLE IF NOT EXISTS `admin` (
    `admin_id`      INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`admin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------
-- worker (작업자)
-- --------------------------------------
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------
-- access_log (출입 로그)
-- --------------------------------------
CREATE TABLE IF NOT EXISTS `access_log` (
    `access_log_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `worker_id`     INT UNSIGNED NOT NULL,
    `checked_at`    DATETIME     NOT NULL,
    `direction`     VARCHAR(10)  NOT NULL COMMENT 'in / out',
    PRIMARY KEY (`access_log_id`),
    KEY `idx_access_log_worker_id` (`worker_id`),
    KEY `idx_access_log_checked_at` (`checked_at`),
    CONSTRAINT `fk_access_log_worker` FOREIGN KEY (`worker_id`) REFERENCES `worker` (`worker_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
