UPDATE match_player
SET deleted_at = %(deleted_at)s
WHERE match_id = (
    SELECT id
    FROM `match`
    WHERE chat_id = %(chat_id)s
    ORDER BY created_at DESC
    LIMIT 1
)
AND player_id = %(player_id)s;