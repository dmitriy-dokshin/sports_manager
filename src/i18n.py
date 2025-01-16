EN = "en"
RU = "ru"

SUPPORTED_LANGUAGES = [EN, RU]


def is_supported_lang(lang):
    return lang in SUPPORTED_LANGUAGES


def invalid_lang(lang):
    if lang == RU:
        return "Некорректное значение языка"
    return "Invalid language value"


def set_lang_success(lang):
    if lang == RU:
        return "Язык успешно изменён"
    return "Language successfully set"
