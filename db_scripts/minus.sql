UPDATE match_player AS p
JOIN user AS u
    ON p.player_id = u.id
SET p.deleted_at = %(deleted_at)s
WHERE p.match_id = %(match_id)s
    AND u.username IN ({});