INSERT INTO match_player (match_id, player_id, created_at, deleted_at, number_of_people, paid)
SELECT %(match_id)s, u.id, %(deleted_at)s, %(deleted_at)s, 1, false
FROM user AS u
WHERE {}
ON DUPLICATE KEY UPDATE
    deleted_at = %(deleted_at)s,
    number_of_people = 1;
