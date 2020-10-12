UPDATE match_player AS p
JOIN user AS u
    ON p.player_id = u.id
SET
    p.paid = true,
    p.updated_at = %(updated_at)s
WHERE p.match_id = %(match_id)s
    AND u.username IN ({});