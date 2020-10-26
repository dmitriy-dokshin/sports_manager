from src.telegram_app import TelegramApp

from flask import Flask
from flask import request
from flask import Response

import os
import ssl

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('sports_manager.pem',
                        'sports_manager.key')
app = Flask(__name__)
telegram_app = TelegramApp()
telegram_bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
host = os.environ["HOST"]
port = int(os.environ["PORT"])


@app.route("/")
def health():
    return Response("I'm OK", content_type="text/plain")


@app.route("/" + telegram_bot_token)
def index():
    with open("update_logger.json", "r") as f:
        return Response(f.read(), content_type="application/json")


@app.route("/bot/" + telegram_bot_token + "/update", methods=["POST"])
def update():
    data = request.get_json()
    telegram_app.update(data)
    return Response(status=200)


if __name__ == "__main__":
    app.run(host=host, port=port, ssl_context=context)
