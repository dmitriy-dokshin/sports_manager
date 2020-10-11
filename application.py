from flask import Flask
from flask import request
from flask import Response

from datetime import datetime
from db import Db

import telegram_api

import json
import os

telegram_bot_token = os.environ["TELEGRAM_BOT_TOKEN"]

app = Flask(__name__)

db = Db()

updates = []


@app.route("/")
def index():
    return Response(json.dumps(updates), content_type="application/json")


def try_parse_int(x, default):
    try:
        return int(x)
    except:
        return default


@app.route("/bot/" + telegram_bot_token + "/update", methods=["POST"])
def update():
    data = request.get_json(force=True)

    updates.append(data)

    if not "message" in data:
        return Response(status=200)
    message = data["message"]
    if not "text" in message:
        return Response(status=200)
    text = message["text"]
    chat_id = message["chat"]["id"]
    created_at = datetime.fromtimestamp(message["date"])
    user = message["from"]

    command = []
    text_parts = text.split("@")
    if text_parts:
        command = text_parts[0].split()

    if not command:
        return Response(status=200)

    if command[0] == "/new":
        db.new_game(user, chat_id, created_at)
    elif command[0] == "/plus" or command[0] == "/plus_paid":
        number_of_people = 1
        if len(command) > 1:
            number_of_people = try_parse_int(command[1], 1)
        paid = command[0] == "/plus_paid"
        db.plus(user, chat_id, created_at,
                number_of_people=number_of_people, paid=paid)
    elif command[0] == "/minus":
        db.minus(user, chat_id, created_at)
    elif command[0] == "/list":
        result = db.list_players(chat_id)
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
        telegram_api.send_message(chat_id, text)

    return Response(status=200)


if __name__ == "__main__":
    app.debug = True
    app.run()
