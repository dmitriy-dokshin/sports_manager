INSERT INTO match_player (match_id, player_id, created_at, number_of_people, paid)
SELECT id, %(player_id)s, %(created_at)s, %(number_of_people)s, %(paid)s
FROM `match`
WHERE chat_id = %(chat_id)s
ORDER BY created_at DESC
LIMIT 1
ON DUPLICATE KEY UPDATE
	updated_at=%(created_at)s,
    number_of_people=%(number_of_people)s,
    paid=%(paid)s;