-- Django migration is the executable schema source. This file is a MySQL 8 reference.
CREATE TABLE IF NOT EXISTS `notifications_center_notificationpublication` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(255) NOT NULL,
  `body` LONGTEXT NOT NULL,
  `level` VARCHAR(20) NOT NULL DEFAULT 'info',
  `target_path` VARCHAR(500) NOT NULL DEFAULT '',
  `audience` VARCHAR(20) NOT NULL DEFAULT 'selected',
  `published_at` DATETIME(6) NULL,
  `sent_count` INT UNSIGNED NOT NULL DEFAULT 0,
  `created_at` DATETIME(6) NOT NULL,
  `created_by_id` BIGINT NOT NULL,
  PRIMARY KEY (`id`),
  KEY `notification_publication_created_by_idx` (`created_by_id`),
  CONSTRAINT `notification_publication_created_by_fk`
    FOREIGN KEY (`created_by_id`) REFERENCES `accounts_user` (`id`)
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `notifications_center_notificationpublication_recipients` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `notificationpublication_id` BIGINT NOT NULL,
  `user_id` BIGINT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `notification_publication_recipient_uniq`
    (`notificationpublication_id`, `user_id`),
  KEY `notification_publication_recipient_user_idx` (`user_id`),
  CONSTRAINT `notification_publication_recipient_publication_fk`
    FOREIGN KEY (`notificationpublication_id`)
    REFERENCES `notifications_center_notificationpublication` (`id`)
    ON DELETE CASCADE,
  CONSTRAINT `notification_publication_recipient_user_fk`
    FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
