-- 博客模块 MySQL 8 参考定义
-- Django migration 是执行源；本文件仅用于评审、DBA 复核或非 Django 部署参考。
-- 字符集：utf8mb4；引擎：InnoDB。

CREATE TABLE IF NOT EXISTS `blog_category` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `name` varchar(100) NOT NULL,
    `slug` varchar(100) NOT NULL,
    `description` longtext NOT NULL,
    `is_enabled` tinyint(1) NOT NULL,
    `sort_order` int(10) unsigned NOT NULL,
    `created_at` datetime(6) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `blog_category_slug_xxx_uniq` (`slug`),
    KEY `blog_catego_slug_fea7ff_idx` (`slug`, `is_enabled`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `blog_tag` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `name` varchar(50) NOT NULL,
    `slug` varchar(50) NOT NULL,
    `is_enabled` tinyint(1) NOT NULL,
    `created_at` datetime(6) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `blog_tag_slug_xxx_uniq` (`slug`),
    KEY `blog_tag_slug_4f1280_idx` (`slug`, `is_enabled`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `blog_author` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `name` varchar(100) NOT NULL,
    `avatar` varchar(100) DEFAULT NULL,
    `bio` longtext NOT NULL,
    `email` varchar(254) NOT NULL DEFAULT '',
    `is_enabled` tinyint(1) NOT NULL,
    `created_at` datetime(6) NOT NULL,
    `user_id` bigint(20) DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `blog_author_is_enab_db801a_idx` (`is_enabled`),
    KEY `blog_author_user_id_xxx_fk` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `blog_post` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `title` varchar(200) NOT NULL,
    `slug` varchar(200) NOT NULL,
    `summary` longtext NOT NULL,
    `content_type` varchar(20) NOT NULL,
    `content_html` longtext DEFAULT NULL,
    `content_markdown` longtext NOT NULL,
    `status` varchar(20) NOT NULL,
    `is_top` tinyint(1) NOT NULL,
    `view_count` int(10) unsigned NOT NULL,
    `sort_order` int(10) unsigned NOT NULL,
    `published_at` datetime(6) DEFAULT NULL,
    `created_at` datetime(6) NOT NULL,
    `updated_at` datetime(6) NOT NULL,
    `cover` varchar(100) DEFAULT NULL,
    `author_id` bigint(20) NOT NULL,
    `category_id` bigint(20) NOT NULL,
    `created_by_id` bigint(20) DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `blog_post_slug_xxx_uniq` (`slug`),
    KEY `blog_post_status_5b2843_idx` (`status`, `published_at`),
    KEY `blog_post_categor_acbd5e_idx` (`category_id`, `status`, `published_at`),
    KEY `blog_post_is_top_1d6c73_idx` (`is_top`, `published_at`),
    KEY `blog_post_sort_or_c380b1_idx` (`sort_order`),
    KEY `blog_post_slug_714acb_idx` (`slug`, `status`),
    KEY `blog_post_author_id_xxx_fk` (`author_id`),
    KEY `blog_post_created_by_id_xxx_fk` (`created_by_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `blog_post_tags` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `post_id` bigint(20) NOT NULL,
    `tag_id` bigint(20) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `blog_post_tags_post_id_tag_id_xxx_uniq` (`post_id`, `tag_id`),
    KEY `blog_post_tags_tag_id_xxx_fk` (`tag_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `blog_postimage` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `image` varchar(100) NOT NULL,
    `caption` varchar(255) NOT NULL,
    `sort_order` int(10) unsigned NOT NULL,
    `created_at` datetime(6) NOT NULL,
    `post_id` bigint(20) NOT NULL,
    PRIMARY KEY (`id`),
    KEY `blog_postimage_post_id_xxx_fk` (`post_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
