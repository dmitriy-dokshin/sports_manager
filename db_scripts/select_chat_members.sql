SELECT
    u.id,
    u.username,
    u.first_name,
    u.last_name,
    u.custom_name,
    p.last_active_at
FROM user AS u
JOIN (
    SELECT
        p.player_id,
        MAX(p.created_at) AS last_active_at
    FROM match_player AS p
    JOIN `match` AS m
        ON p.match_id = m.id
    WHERE
        m.chat_id = %(chat_id)s
    GROUP BY
        p.player_id
) AS p ON p.player_id = u.id
ORDER BY
    p.last_active_at DESC;
