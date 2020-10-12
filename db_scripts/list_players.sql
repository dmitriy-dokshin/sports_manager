SELECT
    u.username,
    u.first_name,
    u.last_name,
    p.number_of_people,
    p.paid
FROM match_player AS p
JOIN user AS u
	ON p.player_id = u.id
WHERE p.match_id = %(match_id)s AND p.deleted_at IS NULL
ORDER BY p.created_at DESC;