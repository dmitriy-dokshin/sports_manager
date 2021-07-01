from src.telegram_app import TelegramApp

from flask import Flask
from flask import request
from flask import Response

import os

app = Flask(__name__)
telegram_app = TelegramApp()
telegram_bot_token = os.environ["TELEGRAM_BOT_TOKEN"]


@app.route("/bot/" + telegram_bot_token + "/update", methods=["POST"])
def update():
    data = request.get_json()
    telegram_app.update(data)
    return Response(status=200)
