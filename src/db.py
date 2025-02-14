from datetime import datetime

import mysql.connector
import os


class Db:
    def __init__(self):
        self.__config = {
            "host": os.environ["DB_HOST"],
            "user": os.environ["DB_USER"],
            "password": os.environ["DB_PASSWORD"],
            "database": "sports_manager",
            "raise_on_warnings": True
        }
        if "DB_SSL_CA" in os.environ:
            self.__config["ssl_ca"] = os.environ["DB_SSL_CA"]
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
        with open("db_scripts/update_chat.sql") as f:
            self.__update_chat_script = f.read()
        with open("db_scripts/update_match_schedule.sql") as f:
            self.__update_match_schedule_script = f.read()
        with open("db_scripts/create_player_stats.sql") as f:
            self.__create_player_stats_script = f.read()
        with open("db_scripts/select_max_matches_count.sql") as f:
            self.__select_max_matches_count_script = f.read()
        with open("db_scripts/select_player_stats.sql") as f:
            self.__select_player_stats_script = f.read()
        with open("db_scripts/select_chat_members.sql") as f:
            self.__select_chat_members_script = f.read()

    def __execute(self, callbacks, cursor_args={"dictionary": True}):
        cnx = mysql.connector.connect(**self.__config)
        cursor = cnx.cursor(**cursor_args)
        try:
            for x in callbacks:
                x(cnx, cursor)
        finally:
            cursor.close()
            cnx.close()

    def __add_or_update_user(self, cursor, user, created_at, custom_name=None):
        data = {
            "id": user["id"],
            "username": user.get("username"),
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
            "custom_name": custom_name,
            "created_at": created_at
        }
        cursor.execute(self.__add_or_update_user_script, data)

    def __find_last_match(self, cursor, chat_id):
        cursor.execute(self.__find_last_match_script, {"chat_id": chat_id})
        for x in cursor:
            return x
        return None

    def __find_last_match_id(self, cursor, chat_id):
        match = self.__find_last_match(cursor, chat_id)
        if match:
            return match["id"]
        return None

    def __build_list_params(self, values, prefix):
        param_data = {}
        param_names = []
        for i, value in enumerate(values):
            param_name = prefix + str(i)
            param_names.append("%({})s".format(param_name))
            param_data[param_name] = value
        return param_data, ", ".join(param_names)

    def find_last_match_age(self, chat_id):
        # That's terrible but I don't know a simple and quick solution now
        result = {}

        def callback(cnx, cursor):
            result["match"] = self.__find_last_match(cursor, chat_id)

        self.__execute([callback])

        if result:
            return datetime.utcnow() - result["match"]["created_at"]
        return None

    def new_game(self, chat_id, created_at, user=None):
        def callback(cnx, cursor):
            owner_id = None
            if user:
                self.__add_or_update_user(cursor, user, created_at)
                owner_id = user["id"]
            script = (
                "INSERT INTO `match` (chat_id, created_at, owner_id)\n"
                "VALUES (%(chat_id)s, %(created_at)s, %(owner_id)s)"
            )
            data = {
                "chat_id": chat_id,
                "created_at": created_at,
                "owner_id": owner_id
            }
            cursor.execute(script, data)
            cnx.commit()

        self.__execute([callback])

    def update_match_schedule(self, chat_id, cron, user, updated_at):
        def callback(cnx, cursor):
            self.__add_or_update_user(cursor, user, updated_at)
            data = {
                "chat_id": chat_id,
                "cron": cron,
                "updated_at": updated_at,
                "owner_id": user["id"]
            }
            cursor.execute(self.__update_match_schedule_script, data)
            cnx.commit()

        self.__execute([callback])

    def set_lang(self, chat_id, lang, user, updated_at):
        def callback(cnx, cursor):
            self.__add_or_update_user(cursor, user, updated_at)
            data = {
                "chat_id": chat_id,
                "lang": lang,
                "updated_at": updated_at,
                "owner_id": user["id"]
            }
            cursor.execute(self.__update_chat_script, data)
            cnx.commit()

        self.__execute([callback])

    def get_lang(self, chat_id):
        result = []

        def callback(cnx, cursor):
            script = "SELECT * FROM chat WHERE chat_id = %(chat_id)s"
            data = {"chat_id": chat_id}
            cursor.execute(script, data)
            result.extend(cursor.fetchall())

        self.__execute([callback])

        return result[0]["lang"] if result else None

    def delete_match_schedule(self, chat_id):
        def callback(cnx, cursor):
            script = "DELETE FROM match_schedule WHERE chat_id = %(chat_id)s"
            data = {"chat_id": chat_id}
            cursor.execute(script, data)
            cnx.commit()

        self.__execute([callback])

    def get_match_schedules(self):
        result = []

        def callback(cnx, cursor):
            script = "SELECT chat_id, cron FROM match_schedule ORDER BY chat_id"
            cursor.execute(script)
            result.extend(cursor.fetchall())

        self.__execute([callback])

        return result

    def plus(self, user, chat_id, created_at, number_of_people=None, paid=False):
        def callback(cnx, cursor):
            match_id = self.__find_last_match_id(cursor, chat_id)
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

    def minus(self, chat_id, deleted_at, user, player_ids=[], usernames=[]):
        def callback(cnx, cursor):
            match_id = self.__find_last_match_id(cursor, chat_id)
            if match_id:
                self.__add_or_update_user(cursor, user, deleted_at)
                if usernames:
                    data, param_names = self.__build_list_params(
                        usernames, "username_")
                    script = self.__minus_script.format(
                        "u.username IN ({})".format(param_names))
                else:
                    data, param_names = self.__build_list_params(
                        player_ids, "player_id_")
                    script = self.__minus_script.format(
                        "u.id IN ({})".format(param_names))
                data["match_id"] = match_id
                data["deleted_at"] = deleted_at
                cursor.execute(script, data)
                cnx.commit()

        self.__execute([callback])

    def paid(self, chat_id, updated_at, player_ids=[], usernames=[]):
        def callback(cnx, cursor):
            match_id = self.__find_last_match_id(cursor, chat_id)
            if match_id:
                if usernames:
                    data, param_names = self.__build_list_params(
                        usernames, "username_")
                    script = self.__paid_script.format(
                        "u.username IN ({})".format(param_names))
                else:
                    data, param_names = self.__build_list_params(
                        player_ids, "player_id_")
                    script = self.__paid_script.format(
                        "p.player_id IN ({})".format(param_names))
                data["match_id"] = match_id
                data["updated_at"] = updated_at
                cursor.execute(script, data)
                cnx.commit()

        self.__execute([callback])

    def list_players(self, chat_id, return_deleted=False):
        result = []

        def callback(cnx, cursor):
            match_id = self.__find_last_match_id(cursor, chat_id)
            if match_id:
                data = {"match_id": match_id}
                cursor.execute(self.__list_players_script, data)
                result.extend(cursor.fetchall())

        self.__execute([callback])

        if not return_deleted:
            result = [x for x in result if not x["deleted_at"]]

        return result

    def get_player_stats(self, chat_id, limit=None):
        result = []

        def create_player_stats(cnx, cursor):
            data = {"chat_id": chat_id}
            cursor.execute(self.__create_player_stats_script, data)

        def select_max_matches_count(cnx, cursor):
            cursor.execute(self.__select_max_matches_count_script)

        def select_player_stats(cnx, cursor):
            script = self.__select_player_stats_script.format("" if not limit else "\nLIMIT {}".format(limit))
            cursor.execute(script)
            result.extend(cursor.fetchall())

        self.__execute([create_player_stats, select_max_matches_count, select_player_stats])

        return result

    def set_custom_name(self, user, custom_name, created_at):
        def callback(cnx, cursor):
            self.__add_or_update_user(cursor, user, created_at, custom_name)
            cnx.commit()

        self.__execute([callback])

    def get_player(self, user):
        result = []

        def callback(cnx, cursor):
            script = "SELECT * FROM user WHERE id = %(user_id)s"
            data = {"user_id": user["id"]}
            cursor.execute(script, data)
            result.extend(cursor.fetchall())

        self.__execute([callback])

        return result[0] if result else None

    def list_chat_members(self, chat_id):
        result = []

        def callback(cnx, cursor):
            data = {"chat_id": chat_id}
            cursor.execute(self.__select_chat_members_script, data)
            result.extend(cursor.fetchall())

        self.__execute([callback])

        return result
