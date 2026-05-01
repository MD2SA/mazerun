import mysql.connector
from mysql.connector import Error

class MySQLConnection:
    def __init__(self, config):
        self.config = config
        self.db = None

    def connect(self):
        import os
        host = os.environ.get("MYSQL_HOST") or self.config.get("host", "localhost")
        try:
            self.db = mysql.connector.connect(
                host=host,
                port=self.config.get("port", 3306),
                user=self.config.get("user", "root"),
                password=self.config.get("password", "root"),
                database=self.config.get("db", "mazerun"),
                auth_plugin="mysql_native_password"
            )
            print(f"[DB] MySQL Connected to {self.config.get('db')} (via {host})")
            return True
        except Error as e:
            print(f"[DB ERROR] {e}")
            return False

    def is_connected(self):
        return self.db and self.db.is_connected()

    def call_sp(self, sp_name, args):
        if not self.is_connected():
            if not self.connect():
                return 0

        cursor = None
        try:
            cursor = self.db.cursor()
            cursor.callproc(sp_name, args)

            result = 0
            for res in cursor.stored_results():
                row = res.fetchone()
                if row:
                    result = row[0]

            self.db.commit()
            return result
        except Error as e:
            print(f"[DB ERROR] SP Call {sp_name}: {e}")
            try:
                self.db.rollback()
            except:
                pass
            return 0
        finally:
            if cursor:
                cursor.close()

    def close(self):
        if self.db:
            self.db.close()
