from src.db import Db
from src.telegram_api import TelegramApi
from src.util import try_parse_int

from collections import deque
from datetime import datetime
from markdown_strings import esc_format

import os
import threading


class TelegramUpdate:
    def __init__(self, data):
        self.bot_command = None
        self.message = data.get("message")
        if not self.message:
            return
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
        self.date = datetime.fromtimestamp(self.message["date"])
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
        self.all_updates = deque(maxlen=512)
        self.__all_updates_lock = threading.Lock()
        self.except_updates = deque(maxlen=512)
        self.__except_updates_lock = threading.Lock()

        self.__db = Db()
        self.__telegram_api = TelegramApi()
        telegram_bot_name = os.environ["TELEGRAM_BOT_NAME"]
        on_update = {
            "/new": self.__new_game,
            "/plus": self.__plus,
            "/plus_paid": self.__plus,
            "/minus": self.__minus,
            "/paid": self.__paid,
            "/list": self.__list,
            "/list_silent": self.__list
        }
        self.__on_update = {}
        for command, handler in on_update.items():
            self.__on_update[command] = handler
            self.__on_update[command + "@" + telegram_bot_name] = handler

    def update(self, data):
        with self.__all_updates_lock:
            self.all_updates.append(data)
        try:
            update = TelegramUpdate(data)
            if update.bot_command:
                handler = self.__on_update.get(update.bot_command)
                if handler:
                    handler(update)
        except:
            with self.__except_updates_lock:
                self.except_updates.append(data)
            raise

    def __new_game(self, update):
        self.__db.new_game(update.user, update.chat_id, update.date)

    def __plus(self, update):
        text_parts = update.text.split()
        number_of_people = try_parse_int(text_parts[-1])
        paid = update.bot_command.startswith("/plus_paid")
        self.__db.plus(
            update.user, update.chat_id, update.date,
            number_of_people=number_of_people,
            paid=paid)

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

    def __list(self, update):
        result = self.__db.list_players(update.chat_id)
        text = ""
        i = 1
        for player in result:
            number_of_people = player["number_of_people"]
            for j in range(0, number_of_people):
                username = player["username"]
                if not username:
                    username = " ".join(
                        [x for x in [player["first_name"], player["last_name"]] if x != None])
                if update.bot_command.startswith("/list_silent"):
                    username = esc_format(username)
                else:
                    username = "[{}](tg://user?id={})".format(
                        username, player["id"])
                row = "{}. {}".format(i + j, username)
                if j > 0:
                    row += " #{}".format(j + 1)
                if player["paid"]:
                    row += " (оплатил)"
                text += row + "\n"
            i += number_of_people
        self.__telegram_api.send_message(
            update.chat_id, text, parse_mode="markdown")
