SELECT id
FROM `match`
WHERE chat_id = %(chat_id)s
ORDER BY created_at DESC
LIMIT 1;