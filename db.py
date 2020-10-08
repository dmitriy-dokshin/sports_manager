import mysql.connector
import os

rds_hostname = os.environ["RDS_HOSTNAME"]
db_admin_password = os.environ["DB_ADMIN_PASSWORD"]

config = {
    "user": "admin",
    "password": db_admin_password,
    "host": rds_hostname,
    "database": "sports_manager",
    "raise_on_warnings": True
}


def connect():
    return mysql.connector.connect(**config)


def new_game(chat_id, created_at):
    cnx = connect()
    cursor = cnx.cursor()
    try:
        script = "INSERT INTO `match` (chat_id, created_at) VALUES (%(chat_id)s, %(created_at)s)"
        data = {"chat_id": chat_id, "created_at": created_at}
        cursor.execute(script, data)
        cnx.commit()
    finally:
        cursor.close()
        cnx.close()


with open("db_scripts/add_or_update_user.sql") as f:
    add_or_update_user_script = f.read()


def add_or_update_user(cursor, user, created_at):
    data = {
        "id": user["id"],
        "username": user["username"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "created_at": created_at
    }
    cursor.execute(add_or_update_user_script, data)


with open("db_scripts/plus.sql") as f:
    plus_script = f.read()


def plus(user, chat_id, created_at, number_of_people=1, paid=False):
    cnx = connect()
    cursor = cnx.cursor()
    try:
        add_or_update_user(cursor, user, created_at)
        data = {
            "chat_id": chat_id,
            "player_id": user["id"],
            "created_at": created_at,
            "number_of_people": number_of_people,
            "paid": paid
        }
        cursor.execute(plus_script, data)
        cnx.commit()
    finally:
        cursor.close()
        cnx.close()


with open("db_scripts/list_players.sql") as f:
    list_players_script = f.read()


def list_players(chat_id):
    cnx = connect()
    cursor = cnx.cursor(dictionary=True)
    try:
        data = {"chat_id": chat_id}
        cursor.execute(list_players_script, data)
        return list(cursor.fetchall())
    finally:
        cursor.close()
        cnx.close()
