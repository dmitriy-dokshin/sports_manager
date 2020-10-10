SELECT
    u.username,
    u.first_name,
    u.last_name,
    p.number_of_people,
    p.paid
FROM match_player AS p
JOIN user AS u
	ON p.player_id = u.id
WHERE p.match_id = (
    SELECT id
    FROM `match`
    WHERE chat_id = %(chat_id)s
    ORDER BY created_at DESC
    LIMIT 1
)
AND p.deleted_at IS NULL
ORDER BY p.created_at DESC;