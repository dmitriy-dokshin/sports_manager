CREATE TEMPORARY TABLE player_stats AS (
    SELECT
        p.player_id,
        COUNT(m.match_id) AS matches_count
    FROM
        match_player AS p
        JOIN (
            SELECT
                *
            FROM
                (
                    SELECT
                        p.match_id,
                        SUM(p.number_of_people) AS `count`
                    FROM
                        match_player AS p
                        JOIN `match` AS m ON p.match_id = m.id
                    WHERE
                        m.chat_id = %(chat_id)s AND p.deleted_at IS NOT NULL
                    GROUP BY
                        p.match_id
                ) AS m
            WHERE
                `count` >= 12
        ) AS m ON p.match_id = m.match_id
    GROUP BY
        p.player_id
);