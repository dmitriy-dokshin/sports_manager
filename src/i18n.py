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

def new_game_will_be_created(lang):
    if lang == RU:
        return "Новая игра будет создана {} (UTC)"
    return "New game will be created at {} (UTC)"

def new_game_created(lang):
    if lang == RU:
        return "Новая игра создана. Записывайтесь!"
    return "New game is created. Sign up!"

def invalid_schedule(lang):
    if lang == RU:
        return "С указанными расписанием что-то не так"
    return "Invalid schedule value"

def invalid_name(lang):
    if lang == RU:
        return "С указанными именем что-то не так"
    return "Invalid name"

def paid(lang):
    if lang == RU:
        return " (оплатил)"
    return " (paid)"

def coming(lang):
    if lang == RU:
        return "Идут:\n"
    return "Coming:\n"

def not_coming(lang):
    if lang == RU:
        return "Не идут:\n"
    return "Not coming:\n"

def we_need_more_people(lang):
    if lang == RU:
        return "Нужно больше людей!"
    return "We need more people!"

def no_more_undecided(lang):
    if lang == RU:
        return "Все определились"
    return "No more undecided"

def we_need_more_gold(lang):
    if lang == RU:
        return "Нужно больше золота!"
    return "We need more gold!"

def everyone_paid(lang):
    if lang == RU:
        return "Все оплатили"
    return "Everyone paid"

def team_1(lang):
    if lang == RU:
        return "Команда 1"
    return "Team 1"

def team_2(lang):
    if lang == RU:
        return "Команда 2"
    return "Team 2"

def name(lang):
    if lang == RU:
        return "Имя"
    return "Name"

def games(lang):
    if lang == RU:
        return "Матчи"
    return "Games"

def votes(lang):
    if lang == RU:
        return "Голоса"
    return "Votes"