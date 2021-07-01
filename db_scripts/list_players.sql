SELECT
    u.id,
    u.username,
    u.first_name,
    u.last_name,
    p.number_of_people,
    p.paid,
    p.deleted_at
FROM match_player AS p
JOIN user AS u
    ON p.player_id = u.id
WHERE p.match_id = %(match_id)s
ORDER BY p.created_at;
