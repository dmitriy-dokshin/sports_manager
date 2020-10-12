def try_parse_int(x, default=None):
    try:
        return int(x)
    except:
        return default