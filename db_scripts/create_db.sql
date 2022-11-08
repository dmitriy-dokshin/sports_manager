CREATE DATABASE IF NOT EXISTS sports_manager
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE sports_manager;

CREATE TABLE IF NOT EXISTS `user` (
    id BIGINT
        NOT NULL
        PRIMARY KEY,
    username VARCHAR(256)
        NULL
        UNIQUE KEY,
    first_name VARCHAR(256)
        NULL,
    last_name VARCHAR(256)
        NULL,
    custom_name VARCHAR(256)
        NULL,
    created_at DATETIME
        NOT NULL,
    updated_at DATETIME
        NULL
)
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `match` (
    id INT UNSIGNED
        NOT NULL
        PRIMARY KEY
        AUTO_INCREMENT,
    chat_id BIGINT
        NOT NULL,
    created_at DATETIME
        NOT NULL,
    owner_id BIGINT
        NULL, -- For scheduling
    CONSTRAINT UNIQUE KEY (chat_id, created_at),
    CONSTRAINT FOREIGN KEY (owner_id)
        REFERENCES `user` (id)
)
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `match_schedule` (
    chat_id BIGINT
        NOT NULL
        PRIMARY KEY,
    cron VARCHAR(256),
    updated_at DATETIME
        NOT NULL,
    owner_id BIGINT
        NOT NULL
)
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `match_player` (
    match_id INT UNSIGNED
        NOT NULL,
    player_id BIGINT
        NOT NULL,
    created_at DATETIME
        NOT NULL,
    updated_at DATETIME
        NULL,
    deleted_at DATETIME
        NULL,
    number_of_people INT UNSIGNED
        NOT NULL,
    paid BOOL
        NOT NULL,
    CONSTRAINT PRIMARY KEY (match_id, player_id),
    CONSTRAINT FOREIGN KEY (match_id)
        REFERENCES `match` (id),
    CONSTRAINT FOREIGN KEY (player_id)
        REFERENCES `user` (id)
)
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
