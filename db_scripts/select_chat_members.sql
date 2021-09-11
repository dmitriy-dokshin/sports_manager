SELECT DISTINCT
    u.id,
    u.username,
    u.first_name,
    u.last_name,
    u.custom_name,
    u.created_at
FROM
    match_player AS p
    JOIN user AS u ON p.player_id = u.id
    JOIN `match` AS m ON p.match_id = m.id
WHERE
    m.chat_id = %(chat_id)s
ORDER BY
    u.created_at;
