INSERT INTO match_schedule (chat_id, cron, updated_at, owner_id)
VALUES (%(chat_id)s, %(cron)s, %(updated_at)s, %(owner_id)s)
ON DUPLICATE KEY UPDATE
    cron=%(cron)s,
    updated_at=%(updated_at)s,
    owner_id=%(owner_id)s;