import json
import requests
import os


class TelegramApi:
    def __init__(self):
        self.__telegram_bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
        self.__base_url = "https://api.telegram.org/bot" + self.__telegram_bot_token

    def send_message(self, chat_id, text, parse_mode=None, reply_markup=None, reply_to_message_id=None):
        data = {"chat_id": chat_id, "text": text}
        if parse_mode:
            data["parse_mode"] = parse_mode
        if reply_markup:
            data["reply_markup"] = reply_markup
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
        print("Starting sending message... ", flush=True)
        print(json.dumps(data), flush=True)
        response = requests.post(self.__base_url + "/sendMessage", json=data, timeout=5)
        print("Message sent", flush=True)
        if response.status_code != 200:
            print(response.content, flush=True)

    def get_chat_member(self, chat_id, user_id):
        params = {"chat_id": chat_id, "user_id": user_id}
        response = requests.get(self.__base_url + "/getChatMember", params=params)
        if response.status_code != 200:
            return None
        return response.json()["result"]
