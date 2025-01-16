INSERT INTO chat (chat_id, lang, updated_at, owner_id)
VALUES (%(chat_id)s, %(lang)s, %(updated_at)s, %(owner_id)s)
ON DUPLICATE KEY UPDATE
    lang=%(lang)s,
    updated_at=%(updated_at)s,
    owner_id=%(owner_id)s;