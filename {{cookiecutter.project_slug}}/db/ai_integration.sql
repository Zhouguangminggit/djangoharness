-- AI 集成模块 MySQL 8 参考定义
-- Django migration 是执行源；本文件仅用于评审、DBA 复核或非 Django 部署参考。
-- 字符集：utf8mb4；引擎：InnoDB。

CREATE TABLE IF NOT EXISTS `ai_integration_aimodelconfig` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `name` varchar(100) NOT NULL,
    `provider` varchar(50) NOT NULL,
    `model_id` varchar(200) NOT NULL,
    `base_url` varchar(200) NOT NULL DEFAULT '',
    `api_key` varchar(500) NOT NULL,
    `timeout` int(10) unsigned NOT NULL DEFAULT 60,
    `is_active` tinyint(1) NOT NULL DEFAULT 1,
    `is_default` tinyint(1) NOT NULL DEFAULT 0,
    `extra_config` json NOT NULL,
    `created_at` datetime(6) NOT NULL,
    `updated_at` datetime(6) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `ai_model_config_provider_name_uniq` (`provider`, `name`),
    KEY `ai_model_config_active_default_idx` (`is_active`, `is_default`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `ai_integration_aigenerationtask` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `task_type` varchar(20) NOT NULL DEFAULT 'video',
    `status` varchar(20) NOT NULL DEFAULT 'pending',
    `prompt` longtext NOT NULL,
    `image` varchar(100) DEFAULT NULL,
    `extra_params` json NOT NULL,
    `external_task_id` varchar(255) NOT NULL DEFAULT '',
    `result_url` varchar(200) NOT NULL DEFAULT '',
    `result_file` varchar(100) DEFAULT NULL,
    `error_message` longtext NOT NULL DEFAULT '',
    `created_at` datetime(6) NOT NULL,
    `started_at` datetime(6) DEFAULT NULL,
    `completed_at` datetime(6) DEFAULT NULL,
    `config_id` bigint(20) NOT NULL,
    `created_by_id` bigint(20) DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `ai_generation_task_status_idx` (`status`),
    KEY `ai_generation_task_config_id_fk` (`config_id`),
    KEY `ai_generation_task_created_by_id_fk` (`created_by_id`),
    CONSTRAINT `ai_generation_task_config_id_fk`
        FOREIGN KEY (`config_id`) REFERENCES `ai_integration_aimodelconfig` (`id`)
        ON DELETE RESTRICT,
    CONSTRAINT `ai_generation_task_created_by_id_fk`
        FOREIGN KEY (`created_by_id`) REFERENCES `accounts_user` (`id`)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
