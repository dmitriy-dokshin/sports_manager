INSERT INTO user (id, username, first_name, last_name, created_at)
VALUES (%(id)s, %(username)s, %(first_name)s, %(last_name)s, %(created_at)s)
ON DUPLICATE KEY UPDATE
	username=%(username)s,
    first_name=%(first_name)s,
    last_name=%(last_name)s,
    updated_at=%(created_at)s;