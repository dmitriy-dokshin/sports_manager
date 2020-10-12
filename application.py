from src.telegram_app import TelegramApp

from flask import Flask
from flask import request
from flask import Response

import json
import os

app = Flask(__name__)
telegram_app = TelegramApp()
telegram_bot_token = os.environ["TELEGRAM_BOT_TOKEN"]


@app.route("/")
def health():
    return Response("I'm OK", content_type="text/plain")


@app.route("/" + telegram_bot_token)
def index():
    data = {
        "all_updates": list(telegram_app.all_updates),
        "except_updates": list(telegram_app.except_updates)
    }
    return Response(json.dumps(data), content_type="application/json")


@app.route("/bot/" + telegram_bot_token + "/update", methods=["POST"])
def update():
    data = request.get_json()
    telegram_app.update(data)
    return Response(status=200)


if __name__ == "__main__":
    app.debug = True
    app.run()
