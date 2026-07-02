-- ============================================================
-- Database Patch Script - Hotel Booking Engine (MySQL)
-- ============================================================
-- Run this in phpMyAdmin → select your database → SQL tab
--
-- COMPATIBILITY:
--   ADD COLUMN IF NOT EXISTS → works on MariaDB 10.2+ (most cPanel hosts)
--   ADD COLUMN IF NOT EXISTS → NOT supported on Oracle MySQL
--   If your host runs Oracle MySQL, use migrate_database.py via SSH instead
--   (check: SELECT VERSION(); in phpMyAdmin SQL tab)
-- ============================================================

-- ── 0. room table: add ac_type if missing ────────────────────
ALTER TABLE `room`
  ADD COLUMN IF NOT EXISTS `ac_type` VARCHAR(10) NOT NULL DEFAULT 'AC';

-- ── 1. user table: add color and role columns ─────────────────
ALTER TABLE `user`
  ADD COLUMN IF NOT EXISTS `color` VARCHAR(7) NOT NULL DEFAULT '#667eea',
  ADD COLUMN IF NOT EXISTS `role`  VARCHAR(20) NOT NULL DEFAULT 'contributor';

-- ── 2. booking table: add adults / children / mattress ────────
ALTER TABLE `booking`
  ADD COLUMN IF NOT EXISTS `status`      VARCHAR(20)  DEFAULT 'active',
  ADD COLUMN IF NOT EXISTS `canceled_at` DATETIME     DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS `comments`    VARCHAR(200) DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS `adults`      INT NOT NULL DEFAULT 1,
  ADD COLUMN IF NOT EXISTS `children`    INT NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS `mattress`    INT NOT NULL DEFAULT 0;

-- Backfill: set status='active' for any existing rows that have NULL
UPDATE `booking` SET `status` = 'active' WHERE `status` IS NULL;

-- ── 3. blocked_room table: add user_id ────────────────────────
ALTER TABLE `blocked_room`
  ADD COLUMN IF NOT EXISTS `user_id` INT DEFAULT NULL;

-- ── 4. booking_group table (create if missing) ────────────────
CREATE TABLE IF NOT EXISTS `booking_group` (
  `id`              INT AUTO_INCREMENT PRIMARY KEY,
  `guest_name`      VARCHAR(100) NOT NULL,
  `guest_phone`     VARCHAR(20)  DEFAULT NULL,
  `id_number`       VARCHAR(50)  DEFAULT NULL,
  `total_amount`    FLOAT        DEFAULT 0,
  `amount_received` FLOAT        DEFAULT 0,
  `payment_mode`    VARCHAR(20)  DEFAULT NULL,
  `receipt_no`      VARCHAR(50)  DEFAULT NULL,
  `booked_by`       VARCHAR(100) DEFAULT NULL,
  `comments`        VARCHAR(200) DEFAULT NULL,
  `checkin`         DATETIME     NOT NULL,
  `checkout`        DATETIME     NOT NULL,
  `status`          VARCHAR(20)  DEFAULT 'active',
  `created_at`      DATETIME     DEFAULT CURRENT_TIMESTAMP,
  INDEX `ix_booking_group_status`   (`status`),
  INDEX `ix_booking_group_checkin`  (`checkin`),
  INDEX `ix_booking_group_checkout` (`checkout`)
);

-- add group_id FK to booking (run after booking_group is created)
ALTER TABLE `booking`
  ADD COLUMN IF NOT EXISTS `group_id` INT DEFAULT NULL;

-- ── 5. room_price table (create if missing) ───────────────────
CREATE TABLE IF NOT EXISTS `room_price` (
  `id`            INT AUTO_INCREMENT PRIMARY KEY,
  `room_id`       INT   NOT NULL,
  `year`          INT   NOT NULL,
  `month`         INT   NOT NULL,
  `price_per_day` FLOAT NOT NULL,
  `created_at`    DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at`    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `unique_room_month_price` (`room_id`, `year`, `month`),
  INDEX `ix_room_price_room_id` (`room_id`),
  INDEX `ix_room_price_year`    (`year`),
  INDEX `ix_room_price_month`   (`month`),
  FOREIGN KEY (`room_id`) REFERENCES `room`(`id`) ON DELETE CASCADE
);

-- ── 6. payment table (create if missing) ─────────────────────
CREATE TABLE IF NOT EXISTS `payment` (
  `id`           INT AUTO_INCREMENT PRIMARY KEY,
  `booking_id`   INT         NOT NULL,
  `amount`       FLOAT       NOT NULL,
  `payment_mode` VARCHAR(20) NOT NULL,
  `receipt_no`   VARCHAR(50) DEFAULT NULL,
  `notes`        VARCHAR(200) DEFAULT NULL,
  `payment_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `created_at`   DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX `ix_payment_booking_id` (`booking_id`),
  FOREIGN KEY (`booking_id`) REFERENCES `booking`(`id`) ON DELETE CASCADE
);

-- ── 7. audit_log table (create if missing) ───────────────────
CREATE TABLE IF NOT EXISTS `audit_log` (
  `id`          INT AUTO_INCREMENT PRIMARY KEY,
  `user_id`     INT          DEFAULT NULL,
  `username`    VARCHAR(50)  DEFAULT NULL,
  `action`      VARCHAR(50)  NOT NULL,
  `entity_type` VARCHAR(20)  NOT NULL,
  `entity_id`   INT          DEFAULT NULL,
  `details`     VARCHAR(500) DEFAULT NULL,
  `created_at`  DATETIME     DEFAULT CURRENT_TIMESTAMP,
  INDEX `ix_audit_log_action`     (`action`),
  INDEX `ix_audit_log_created_at` (`created_at`),
  FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE SET NULL
);

-- ── 8. Indexes (MySQL-safe: uses a stored procedure to skip  ──
--        existing indexes instead of IF NOT EXISTS)            ──
DROP PROCEDURE IF EXISTS _create_index_if_missing;
DELIMITER //
CREATE PROCEDURE _create_index_if_missing(
  tbl VARCHAR(64), idx VARCHAR(64), col VARCHAR(64)
)
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name   = tbl
      AND index_name   = idx
  ) THEN
    SET @sql = CONCAT('CREATE INDEX `', idx, '` ON `', tbl, '`(`', col, '`)');
    PREPARE s FROM @sql;
    EXECUTE s;
    DEALLOCATE PREPARE s;
  END IF;
END //
DELIMITER ;

CALL _create_index_if_missing('booking',      'ix_booking_status',       'status');
CALL _create_index_if_missing('booking',      'ix_booking_checkin',      'checkin');
CALL _create_index_if_missing('booking',      'ix_booking_checkout',     'checkout');
CALL _create_index_if_missing('booking',      'ix_booking_room_id',      'room_id');
CALL _create_index_if_missing('booking',      'ix_booking_group_id',     'group_id');
CALL _create_index_if_missing('blocked_room', 'ix_blocked_room_user_id', 'user_id');

DROP PROCEDURE IF EXISTS _create_index_if_missing;

-- ============================================================
-- Done. Restart the application after running this script.
-- (In cPanel: touch passenger_wsgi.py  OR  restart the app
--  from the "Setup Python App" section)
-- ============================================================
