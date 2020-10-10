import requests
import os

telegram_bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
base_url = "https://api.telegram.org/bot" + telegram_bot_token
send_message_url = base_url + "/sendMessage"


def send_message(chat_id, text):
    requests.post(send_message_url, json={"chat_id": chat_id, "text": text})
