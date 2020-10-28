INSERT INTO match_player (match_id, player_id, created_at, number_of_people, paid)
VALUES (%(match_id)s, %(player_id)s, %(created_at)s, IFNULL(%(number_of_people)s, 1), %(paid)s)
ON DUPLICATE KEY UPDATE
    updated_at=%(created_at)s,
    deleted_at=NULL,
    number_of_people=IFNULL(%(number_of_people)s, number_of_people),
    paid=%(paid)s;