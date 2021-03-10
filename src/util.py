from markdown_strings import esc_format

import unicodedata

def try_parse_int(x, default=None):
    try:
        return int(x)
    except:
        return default


def is_bidirectional(text):
    return any(unicodedata.bidirectional(x) in ('R', 'AL') for x in text)


def get_full_name(player):
    full_name = " ".join(x for x in [player["first_name"], player["last_name"]] if x != None)
    if is_bidirectional(full_name):
        return "..."
    else:
        return full_name  


def get_username(player, silent):
    username = player["username"]
    if not username:
        username = get_full_name(player)
    if silent:
        username = esc_format(username)
    else:
        username = "[{}](tg://user?id={})".format(username, player["id"])
    return username
