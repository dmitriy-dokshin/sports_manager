import requests
import os


class TelegramApi:
    def __init__(self):
        self.__telegram_bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
        self.__base_url = "https://api.telegram.org/bot" + self.__telegram_bot_token
        self.__send_message_url = self.__base_url + "/sendMessage"

    def send_message(self, chat_id, text, parse_mode):
        result = requests.post(
            self.__send_message_url,
            json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode})
