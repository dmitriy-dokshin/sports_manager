from src.db import Db
from src.telegram_api import TelegramApi
from src.util import try_parse_int
from src.util import get_full_name
from src.util import get_username

from collections import deque
from concurrent.futures import ThreadPoolExecutor
from croniter import croniter
from datetime import datetime
from datetime import timedelta

import asyncio
import atexit
import json
import os
import random
import threading


class Scheduler:
    def __init__(self):
        self.__lock = threading.RLock()
        self.__executor = ThreadPoolExecutor(max_workers=32)
        self.__cancellation_events = {}

        def sigint_handler():
            for event in self.__cancellation_events.values():
                event.set()
        atexit.register(sigint_handler)

    def run(self, key, callback):
        with self.__lock:
            self.cancel(key)
            cancellation_event = threading.Event()
            self.__cancellation_events[key] = cancellation_event
            self.__executor.submit(callback, cancellation_event)

    def cancel(self, key):
        with self.__lock:
            cancellation_event = self.__cancellation_events.get(key)
            if cancellation_event:
                cancellation_event.set()


class TelegramUpdate:
    def __init__(self, data):
        print(json.dumps(data), flush=True)

        self.bot_command = None
        self.data = None

        callback_query = data.get("callback_query")
        if callback_query:
            self.data = callback_query["data"]
            try:
                self.data = json.loads(self.data)
            except:
                pass
            if isinstance(self.data, list) and len(self.data) > 0:
                self.bot_command = self.data[0]
            else:
                self.data = None
            self.message = callback_query["message"]
            self.chat_id = self.message["chat"]["id"]
            self.date = datetime.now()
            self.user = callback_query["from"]
            return

        self.message = data.get("message")
        if not self.message:
            return
        self.message_id = self.message["message_id"]
        self.text = self.message.get("text")
        if not self.text:
            return
        self.mentions = []
        self.text_mentions = []
        if "entities" in self.message:
            for entity in self.message["entities"]:
                def get_entity():
                    return self.text[entity["offset"]:][:entity["length"]]
                entity_type = entity["type"]
                if entity_type == "bot_command":
                    self.bot_command = get_entity()
                if entity_type == "mention":
                    self.mentions.append(get_entity())
                if entity_type == "text_mention":
                    self.text_mentions.append(entity["user"])
        self.chat_id = self.message["chat"]["id"]
        self.date = datetime.utcfromtimestamp(self.message["date"])
        self.user = self.message["from"]

    def get_usernames(self):
        usernames = []
        if self.mentions:
            for x in self.mentions:
                usernames.append(x[1:])
        return usernames

    def get_user_ids(self):
        user_ids = []
        if self.text_mentions:
            for x in self.text_mentions:
                user_ids.append(x["id"])
        else:
            user_ids.append(self.user["id"])
        return user_ids


class TelegramApp:
    def __init__(self):
        self.__db = Db()
        self.__telegram_api = TelegramApi()
        telegram_bot_name = os.environ["TELEGRAM_BOT_NAME"]
        on_update = {
            "/new": self.__new_game,
            "/set_schedule": self.__set_schedule,
            "/delete_schedule": self.__delete_schedule,
            "/plus": self.__plus,
            "/plus_paid": self.__plus,
            "/minus": self.__minus,
            "/paid": self.__plus,
            "/list": self.__list,
            "/list_aloud": self.__list,
            "/random_teams": self.__random_teams,
            "/player_stats": self.__player_stats,
            "/help": self.__help,
            "/help_admin": self.__help_admin
        }
        self.__on_update = {}
        for command, handler in on_update.items():
            self.__on_update[command] = handler
            self.__on_update[command + "@" + telegram_bot_name] = handler

        self.__admins = set(["da_life", "dmitriy_dokshin"])
        self.__alert_match_age = False

        with open("bot_help.txt") as f:
            self.__bot_help = f.read()
        with open("bot_help_admin.txt") as f:
            self.__bot_help_admin = f.read()

        self.__scheduler = Scheduler()
        for x in self.__db.get_match_schedules():
            chat_id = x["chat_id"]
            cron = x["cron"]
            self.__schedule_impl(chat_id, cron)

    def update(self, data):
        update = TelegramUpdate(data)
        if update.bot_command:
            handler = self.__on_update.get(update.bot_command)
            if handler:
                handler(update)

    def __new_game(self, update):
        username = update.user.get("username")
        if not self.__admins or username in self.__admins:
            self.__db.new_game(update.chat_id, update.date, update.user)

    def __schedule_impl(self, chat_id, cron):
        iter = croniter(cron, datetime.utcnow())

        def callback(cancellation_event):
            while True:
                created_at = iter.get_next(datetime)
                print("Новая игра для чата {} будет создана {}".format(
                    chat_id, created_at), flush=True)
                t = (created_at - datetime.utcnow()).total_seconds()
                if cancellation_event.wait(t):
                    break
                else:
                    self.__db.new_game(chat_id, created_at)
                    self.__telegram_api.send_message(
                        chat_id, "Новая игра создана. Записывайтесь!")

        self.__scheduler.run(chat_id, callback)

    def __set_schedule(self, update):
        text_parts = update.text.split()
        cron = None
        if len(text_parts) > 1:
            cron_text = " ".join(text_parts[1:])
            if croniter.is_valid(cron_text):
                cron = cron_text

        if cron:
            self.__schedule_impl(update.chat_id, cron)
            self.__db.update_match_schedule(
                update.chat_id, cron, update.user, update.date)
        else:
            self.__telegram_api.send_message(
                update.chat_id, "С указанным cron выражением что-то не так")

    def __delete_schedule(self, update):
        self.__scheduler.cancel(update.chat_id)
        self.__db.delete_match_schedule(update.chat_id)

    def __plus(self, update):
        if self.__alert_match_age:
            match_age = self.__db.find_last_match_age(update.chat_id)
            if match_age and match_age > timedelta(days=7):
                self.__telegram_api.send_message(
                    update.chat_id, "Забыли создать новую игру? /new")

        number_of_people = None
        if update.data and len(update.data) > 1:
            number_of_people = update.data[1]
            if not isinstance(number_of_people, int):
                number_of_people = None

        paid_commands = ["/plus_paid", "/paid"]
        paid = any(x for x in paid_commands if update.bot_command.startswith(x))

        self.__db.plus(
            update.user, update.chat_id, update.date,
            number_of_people=number_of_people,
            paid=paid)

        if not number_of_people:
            buttons = []
            for x in range(1, 5):
                buttons.append({"text": str(x), "callback_data": json.dumps([update.bot_command, x])})
            reply_markup = {"inline_keyboard": [buttons]}
            self.__telegram_api.send_message(
                update.chat_id, "Если надо, можно указать количество людей, включая тебя",
                reply_markup=reply_markup,
                reply_to_message_id=update.message_id)


    def __minus(self, update):
        self.__db.minus(
            update.chat_id, update.date,
            player_ids=update.get_user_ids(),
            usernames=update.get_usernames())

    def __paid(self, update):
        self.__db.paid(
            update.chat_id, update.date,
            player_ids=update.get_user_ids(),
            usernames=update.get_usernames())

    def __print_players(self, update, players, text):
        i = 1
        for player in players:
            number_of_people = player["number_of_people"]
            for j in range(0, number_of_people):
                username = get_username(
                    player, silent=not update.bot_command.startswith("/list_aloud"))
                row = "{}. {}".format(i + j, username)
                if number_of_people > 1:
                    row += " #{}".format(j + 1)
                if player["paid"]:
                    row += " (оплатил)"
                text += row + "\n"
            i += number_of_people
        return text


    def __list(self, update):
        players = self.__db.list_players(update.chat_id, return_deleted=True)
        text = ""

        plus_players = [x for x in players if not x["deleted_at"]]
        if plus_players:
            text += "Идут:\n"
            text = self.__print_players(update, plus_players, text)

        minus_players = [x for x in players if x["deleted_at"]]
        if minus_players:
            if plus_players:
                text += "\n"
            text += "Не идут:\n"
            text = self.__print_players(update, minus_players, text)

        self.__telegram_api.send_message(
            update.chat_id, text, parse_mode="markdown")


    def __random_teams(self, update):
        players = self.__db.list_players(update.chat_id)
        random.shuffle(players)
        team1 = []
        team2 = []
        for player in players:
            number_of_people = player["number_of_people"]
            team_flag = len(team1) < len(players) / 2
            for j in range(0, number_of_people):
                username = get_username(player, silent=True)
                if j > 0:
                    username += " #{}".format(j + 1)
                if team_flag:
                    team1.append(username)
                else:
                    team2.append(username)

        def print_team(team, title):
            text = title
            for i, player in enumerate(team):
                text += "\n{}. {}".format(i + 1, player)
            return text

        text = print_team(team1, "Команда 1") + "\n\n" + \
            print_team(team2, "Команда 2")

        self.__telegram_api.send_message(
            update.chat_id, text, parse_mode="markdown")

    def __player_stats(self, update):
        players = self.__db.get_player_stats(update.chat_id)
        headers = ["#", "Username", "Имя", "Матчи", "Голоса для опроса"]
        max_lens = [len(x) for x in headers]
        rows = []
        i = 1
        for player in players:
            row = [
                str(i),
                player["username"] or "NULL",
                get_full_name(player) or "NULL",
                str(player["matches_count"]),
                str(player["poll_votes_count"])
            ]
            for j, x in enumerate(row, 0):
                max_lens[j] = max(max_lens[j], len(x))
            rows.append(row)
            i += 1

        def build_row(row, space=" ", frame="|"):
            result = (space + frame + space).join(
                x + (" " * (max_lens[j] - len(x))) for j, x in enumerate(row, 0))
            return space.join([frame, result, frame])

        row_delimiter = build_row(("-" * x for x in max_lens), space="-", frame="+")
        final_rows = [
            row_delimiter,
            build_row(headers),
            row_delimiter
        ]
        for row in rows:
            final_rows.append(build_row(row))
        final_rows.append(row_delimiter)
        
        text = "```\n{}\n```".format("\n".join(final_rows))

        self.__telegram_api.send_message(
            update.chat_id, text, parse_mode="markdown")

    def __help(self, update):
        self.__telegram_api.send_message(update.chat_id, self.__bot_help)

    def __help_admin(self, update):
        self.__telegram_api.send_message(update.chat_id, self.__bot_help_admin)
