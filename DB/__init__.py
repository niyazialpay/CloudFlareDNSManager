import os
import sqlite3
from DB import regex_data

regex = regex_data.regex_data()


class DB:

    def __init__(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.__db_file = self.dir_path + "/system.db"
        self.__connection = sqlite3.connect(self.__db_file, check_same_thread=False)
        self.__connection.row_factory = sqlite3.Row
        self.__db = self.__connection.cursor()
        self.create_table()

    def __del__(self):
        self.__db.close()
        self.__connection.close()

    def create_table(self):
        self.__db.execute("CREATE TABLE IF NOT EXISTS api_key (id INTEGER PRIMARY KEY, email TEXT, api_key TEXT)")
        self.__db.execute(
            "CREATE TABLE IF NOT EXISTS tmp_data (id INTEGER PRIMARY KEY, zone_id TEXT, dns_id TEXT, dns_type TEXT)")
        self.__db.execute(
            "CREATE TABLE IF NOT EXISTS under_attack (id INTEGER PRIMARY KEY, zone_id TEXT, dns_id TEXT, dns_type TEXT, dns_name TEXT, dns_content TEXT, dns_proxied TEXT, security_level TEXT)")
        self.__db.execute("CREATE TABLE IF NOT EXISTS dns_resolver (id INTEGER PRIMARY KEY, ip TEXT)")
        self.__connection.commit()
        if len(self.get_resolver_list()) == 0:
            self.insert_resolver("1.1.1.1")

    def select_api(self):
        self.__db.execute("select * from api_key where id=1 limit 1")
        result = self.__db.fetchone()
        if result is not None:
            result.keys()
            return result
        else:
            return None

    def insert_api(self, email, api_key):
        try:
            if self.select_api() is not None:
                self.__db.execute("update api_key set email=?, api_key=?", (regex.string(email), regex.string(api_key)))
            else:
                self.__db.execute("insert into api_key (email, api_key) values (?, ?)",
                                  (regex.string(email), regex.string(api_key)))
            self.__connection.commit()
            return True
        except:
            return False

    def select_tmp_data(self):
        self.__db.execute("select * from tmp_data where id=1 limit 1")
        result = self.__db.fetchone()
        if result is not None:
            result.keys()
            return result
        else:
            return None

    def insert_tmp_data(self, zone_id, dns_id="", dns_type=""):
        try:
            if self.select_tmp_data() is not None:
                self.__db.execute("update tmp_data set zone_id=?, dns_id=?, dns_type=?",
                                  (regex.string(zone_id), regex.string(dns_id), regex.string(dns_type)))
            else:
                self.__db.execute("insert into tmp_data (zone_id, dns_id, dns_type) values (?,?, ?)",
                                  (regex.string(zone_id), regex.string(dns_id), regex.string(dns_type)))
            self.__connection.commit()
            return True
        except:
            return False

    def insert_under_attack(self, zone_id, dns_id, dns_type, dns_name, dns_content, dns_proxied, security_level):
        try:
            self.__db.execute(
                "insert into under_attack (zone_id, dns_id, dns_type, dns_name, dns_content, dns_proxied, security_level) values (?,?,?,?,?,?,?)",
                (regex.string(zone_id), regex.string(dns_id), regex.string(dns_type), regex.string(dns_name),
                 regex.string(dns_content), regex.string(dns_proxied), regex.string(security_level)))
            self.__connection.commit()
            return True
        except:
            return False

    def select_under_attack(self, zone_id):
        self.__db.execute("select * from under_attack where zone_id=?", (regex.string(zone_id),))
        result = self.__db.fetchall()
        if result is not None:
            return result
        else:
            return None

    def remove_under_attack(self, zone_id):
        self.__db.execute("delete from under_attack where zone_id=?", (regex.string(zone_id),))
        self.__connection.commit()

    def get_resolver_list(self):
        self.__db.execute("select * from dns_resolver")
        result = self.__db.fetchall()
        if result is not None:
            return result
        else:
            return None

    def insert_resolver(self, ip):
        try:
            self.__db.execute("insert into dns_resolver (ip) values (?)", (ip,))
            self.__connection.commit()
            return True
        except:
            return False

    def remove_resolver(self, ip):
        self.__db.execute("delete from dns_resolver where ip=?", (ip,))
        self.__connection.commit()
