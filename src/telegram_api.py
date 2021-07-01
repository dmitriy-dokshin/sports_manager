import requests
import os


class TelegramApi:
    def __init__(self):
        self.__telegram_bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
        self.__base_url = "https://api.telegram.org/bot" + self.__telegram_bot_token
        self.__send_message_url = self.__base_url + "/sendMessage"

    def send_message(self, chat_id, text, parse_mode=None, reply_markup=None, reply_to_message_id=None):
        data = {"chat_id": chat_id, "text": text}
        if parse_mode:
            data["parse_mode"] = parse_mode
        if reply_markup:
            data["reply_markup"] = reply_markup
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
        requests.post(self.__send_message_url, json=data)
