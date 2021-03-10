SET
    @max_matches_count := (
        SELECT
            MAX(matches_count)
        FROM
            player_stats
    );