SELECT
    u.username,
    u.first_name,
    u.last_name,
    mp.number_of_people,
    mp.paid
FROM match_player AS mp
JOIN user AS u
	ON mp.player_id = u.id
WHERE match_id = (
    SELECT id
    FROM `match`
    WHERE chat_id = %(chat_id)s
    ORDER BY created_at DESC
    LIMIT 1
)
ORDER BY mp.created_at DESC;