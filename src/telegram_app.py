from src.db import Db
from src.telegram_api import TelegramApi
from src.util import try_parse_int

from datetime import datetime

import os
import threading


class TelegramUpdate:
    def __init__(self, data):
        self.message = data.get("message")
        if self.message:
            self.text = self.message["text"]
            self.mentions = []
            if "entities" in self.message:
                for entity in self.message["entities"]:
                    def get_entity():
                        return self.text[entity["offset"]:][:entity["length"]]
                    entity_type = entity["type"]
                    if entity_type == "bot_command":
                        self.bot_command = get_entity()
                    if entity_type == "mention":
                        self.mentions.append(get_entity())
            self.chat_id = self.message["chat"]["id"]
            self.date = datetime.fromtimestamp(self.message["date"])
            self.user = self.message["from"]


class TelegramApp:
    def __init__(self):
        self.all_updates = []
        self.__all_updates_lock = threading.Lock()
        self.except_updates = []
        self.__except_updates_lock = threading.Lock()

        self.__db = Db()
        self.__telegram_api = TelegramApi()
        telegram_bot_name = os.environ["TELEGRAM_BOT_NAME"]
        on_update = {
            "/new": self.__new_game,
            "/plus": self.__plus,
            "/plus_paid": self.__plus,
            "/minus": self.__minus,
            "/list": self.__list
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
        usernames = []
        if update.mentions:
            for x in update.mentions:
                usernames.append(x[1:])
        else:
            usernames.append(update.user["username"])
        self.__db.minus(usernames, update.chat_id, update.date)

    def __list(self, update):
        result = self.__db.list_players(update.chat_id)
        text = ""
        i = 1
        for x in result:
            for j in range(0, x["number_of_people"]):
                row = "{}. @{}".format(i + j, x["username"])
                if j > 0:
                    row += " #{}".format(j + 1)
                if x["paid"]:
                    row += " (оплатил)"
                text += row + "\n"
            i += 1
        print(text)
        self.__telegram_api.send_message(update.chat_id, text)
