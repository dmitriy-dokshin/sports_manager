UPDATE match_player
SET deleted_at = %(deleted_at)s
WHERE match_id = %(match_id)s AND player_id = %(player_id)s;