from flask import Flask
from flask import request
from flask import Response

from datetime import datetime

import db

import json
import os

telegram_bot_token = os.environ["TELEGRAM_BOT_TOKEN"]

app = Flask(__name__)

global_chat_id = -219063945


@app.route("/")
def index():
    return Response(json.dumps(db.list_players(chat_id=global_chat_id)))


@app.route("/bot/" + telegram_bot_token + "/update", methods=["POST"])
def update():
    global global_chat_id

    data = request.get_json()

    message = data["message"]
    text = message["text"]
    chat_id = message["chat"]["id"]
    created_at = datetime.fromtimestamp(message["date"])
    user = message["from"]

    if text == "/new@sports_manager_bot":
        db.new_game(chat_id, created_at)
    elif text == "/plus@sports_manager_bot":
        db.plus(user, chat_id, created_at)
    elif text == "/list@sports_manager_bot":
        global_chat_id = chat_id

    return Response(status=200)


if __name__ == "__main__":
    app.debug = True
    app.run()
