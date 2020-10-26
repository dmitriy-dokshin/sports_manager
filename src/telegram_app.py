from src.db import Db
from src.telegram_api import TelegramApi
from src.util import try_parse_int
from src.util import get_username

from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import asyncio
import json
import os
import random
import threading


class UpdateLogger:
    def __init__(self):
        self.__ok_updates = deque(maxlen=512)
        self.__except_updates = deque(maxlen=512)
        self.__lock = threading.Lock()
        self.__executor = ThreadPoolExecutor(max_workers=1)

    def __save(self):
        with self.__lock:
            data = {
                "ok_updates": list(self.__ok_updates),
                "except_updates": list(self.__except_updates)
            }
            json_data = json.dumps(data)
            with open("update_logger.json", "w") as f:
                f.write(json_data)

    def log(self, data, is_except=False):
        with self.__lock:
            if is_except:
                self.__except_updates.append(data)
            else:
                self.__ok_updates.append(data)
        self.__executor.submit(self.__save)


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
        self.__logger = UpdateLogger()
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
            "/list_silent": self.__list,
            "/random_teams": self.__random_teams,
            "/help": self.__help,
            "/help_admin": self.__help_admin,
        }
        self.__on_update = {}
        for command, handler in on_update.items():
            self.__on_update[command] = handler
            self.__on_update[command + "@" + telegram_bot_name] = handler

        self.__admins = set(["da_life", "dmitriy_dokshin"])

        with open("bot_help.txt") as f:
            self.__bot_help = f.read()
        with open("bot_help_admin.txt") as f:
            self.__bot_help_admin = f.read()

    def update(self, data):
        try:
            update = TelegramUpdate(data)
            if update.bot_command:
                handler = self.__on_update.get(update.bot_command)
                if handler:
                    handler(update)
            self.__logger.log(data)
        except:
            self.__logger.log(data, is_except=True)

    def __new_game(self, update):
        username = update.user.get("username")
        if username in self.__admins:
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
        players = self.__db.list_players(update.chat_id)
        text = ""
        i = 1
        for player in players:
            number_of_people = player["number_of_people"]
            for j in range(0, number_of_people):
                username = get_username(
                    player, silent=update.bot_command.startswith("/list_silent"))
                row = "{}. {}".format(i + j, username)
                if j > 0:
                    row += " #{}".format(j + 1)
                if player["paid"]:
                    row += " (оплатил)"
                text += row + "\n"
            i += number_of_people
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

    def __help(self, update):
        self.__telegram_api.send_message(update.chat_id, self.__bot_help)

    def __help_admin(self, update):
        self.__telegram_api.send_message(update.chat_id, self.__bot_help_admin)
