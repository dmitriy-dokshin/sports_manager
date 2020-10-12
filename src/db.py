import mysql.connector
import os


class Db:
    def __init__(self):
        self.__config = {
            "user": "admin",
            "password": os.environ["DB_ADMIN_PASSWORD"],
            "host": os.environ["RDS_HOSTNAME"],
            "database": "sports_manager",
            "raise_on_warnings": True
        }
        with open("db_scripts/add_or_update_user.sql") as f:
            self.__add_or_update_user_script = f.read()
        with open("db_scripts/plus.sql") as f:
            self.__plus_script = f.read()
        with open("db_scripts/minus.sql") as f:
            self.__minus_script = f.read()
        with open("db_scripts/paid.sql") as f:
            self.__paid_script = f.read()
        with open("db_scripts/list_players.sql") as f:
            self.__list_players_script = f.read()
        with open("db_scripts/find_last_match.sql") as f:
            self.__find_last_match_script = f.read()

    def __execute(self, callbacks, cursor_args={"dictionary": True}):
        cnx = mysql.connector.connect(**self.__config)
        cursor = cnx.cursor(**cursor_args)
        try:
            for x in callbacks:
                x(cnx, cursor)
        finally:
            cursor.close()
            cnx.close()

    def __add_or_update_user(self, cursor, user, created_at):
        data = {
            "id": user["id"],
            "username": user["username"],
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
            "created_at": created_at
        }
        cursor.execute(self.__add_or_update_user_script, data)

    def __find_last_match(self, cursor, chat_id):
        cursor.execute(self.__find_last_match_script, {"chat_id": chat_id})
        for x in cursor:
            return x["id"]
        return None

    def __build_list_params(self, values, prefix):
        param_data = {}
        param_names = []
        for i, value in enumerate(values):
            param_name = prefix + str(i)
            param_names.append("%({})s".format(param_name))
            param_data[param_name] = value
        return param_data, ", ".join(param_names)

    def new_game(self, user, chat_id, created_at):
        def callback(cnx, cursor):
            self.__add_or_update_user(cursor, user, created_at)
            script = (
                "INSERT INTO `match` (chat_id, created_at, owner_id)\n"
                "VALUES (%(chat_id)s, %(created_at)s, %(owner_id)s)"
            )
            data = {
                "chat_id": chat_id,
                "created_at": created_at,
                "owner_id": user["id"]

            }
            cursor.execute(script, data)
            cnx.commit()

        self.__execute([callback])

    def plus(self, user, chat_id, created_at, number_of_people=None, paid=False):
        def callback(cnx, cursor):
            match_id = self.__find_last_match(cursor, chat_id)
            if match_id:
                self.__add_or_update_user(cursor, user, created_at)
                data = {
                    "match_id": match_id,
                    "player_id": user["id"],
                    "created_at": created_at,
                    "number_of_people": number_of_people,
                    "paid": paid
                }
                cursor.execute(self.__plus_script, data)
                cnx.commit()

        self.__execute([callback])

    def minus(self, usernames, chat_id, deleted_at):
        def callback(cnx, cursor):
            match_id = self.__find_last_match(cursor, chat_id)
            if match_id:
                data, param_names = self.__build_list_params(
                    usernames, "username_")
                data["match_id"] = match_id
                data["deleted_at"] = deleted_at
                script = self.__minus_script.format(param_names)
                cursor.execute(script, data)
                cnx.commit()

        self.__execute([callback])

    def paid(self, usernames, chat_id, updated_at):
        def callback(cnx, cursor):
            match_id = self.__find_last_match(cursor, chat_id)
            if match_id:
                data, param_names = self.__build_list_params(
                    usernames, "username_")
                data["match_id"] = match_id
                data["updated_at"] = updated_at
                script = self.__paid_script.format(param_names)
                cursor.execute(script, data)
                cnx.commit()

        self.__execute([callback])

    def list_players(self, chat_id):
        result = []

        def callback(cnx, cursor):
            match_id = self.__find_last_match(cursor, chat_id)
            if match_id:
                data = {"match_id": match_id}
                cursor.execute(self.__list_players_script, data)
                result.extend(cursor.fetchall())

        self.__execute([callback])

        return result
