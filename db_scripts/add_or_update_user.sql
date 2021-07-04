INSERT INTO user (id, username, first_name, last_name, custom_name, created_at)
VALUES (%(id)s, %(username)s, %(first_name)s, %(last_name)s, %(custom_name)s, %(created_at)s)
ON DUPLICATE KEY UPDATE
    username=%(username)s,
    first_name=%(first_name)s,
    last_name=%(last_name)s,
    custom_name=IFNULL(%(custom_name)s, custom_name),
    updated_at=%(created_at)s;
