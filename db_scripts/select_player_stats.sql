SELECT
    u.id,
    u.username,
    u.first_name,
    u.last_name,
    u.custom_name,
    matches_count,
    CEILING(p.matches_count / @max_matches_count * 5.0) AS poll_votes_count
FROM
    player_stats AS p
    JOIN user AS u ON p.player_id = u.id
ORDER BY
    p.matches_count DESC{};
