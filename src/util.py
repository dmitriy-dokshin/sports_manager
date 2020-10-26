from markdown_strings import esc_format


def try_parse_int(x, default=None):
    try:
        return int(x)
    except:
        return default


def get_username(player, silent):
    username = player["username"]
    if not username:
        username = " ".join(
            [x for x in [player["first_name"], player["last_name"]] if x != None])
    if silent:
        username = esc_format(username)
    else:
        username = "[{}](tg://user?id={})".format(username, player["id"])
    return username
