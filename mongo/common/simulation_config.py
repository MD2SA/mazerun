from datetime import datetime, timezone
from decimal import Decimal

import mysql.connector
from mysql.connector import Error


CONFIG_FIELDS = [
    "numbermarsamis",
    "numberrooms",
    "numberplayers",
    "normalnoise",
    "noisevartoleration",
    "normaltemperature",
    "temperaturevarhightoleration",
    "temperaturevarlowtoleration",
]


class SimulationConfigRepository:
    def __init__(self, db, mysql_config=None):
        self.db = db
        self.mysql_config = mysql_config or {}
        self.collection = db["simulation_configs"]

    def get_or_fetch(self, simulation_id):
        cached = self.collection.find_one({"_id": simulation_id})
        if cached:
            return cached

        fetched = self.fetch_from_mysql()
        if not fetched:
            return None

        return self.save(simulation_id, fetched)

    def save(self, simulation_id, values):
        doc = {
            "_id": simulation_id,
            "loaded_at": datetime.now(timezone.utc),
            **values,
        }
        self.collection.update_one({"_id": simulation_id}, {"$set": doc}, upsert=True)
        return doc

    def fetch_from_mysql(self):
        try:
            connection = mysql.connector.connect(
                host=self.mysql_config.get("host", "194.210.86.10"),
                port=self.mysql_config.get("port", 3306),
                user=self.mysql_config.get("user", "aluno"),
                password=self.mysql_config.get("password", "aluno"),
                database=self.mysql_config.get("db", "maze"),
                auth_plugin="mysql_native_password",
            )
            cursor = connection.cursor(dictionary=True)
            table_name = self._find_config_table(cursor)
            if not table_name:
                print("[SimulationConfig] No MySQL table found with expected config columns.")
                return None

            columns = ", ".join(f"`{field}`" for field in CONFIG_FIELDS)
            cursor.execute(f"SELECT {columns} FROM `{table_name}` LIMIT 1")
            row = cursor.fetchone()
            if not row:
                print(f"[SimulationConfig] Table {table_name} has no config rows.")
                return None

            return {field: self._normalise_value(row.get(field)) for field in CONFIG_FIELDS}
        except Error as e:
            print(f"[SimulationConfig] MySQL error loading simulation config: {e}")
            return None
        finally:
            try:
                cursor.close()
                connection.close()
            except Exception:
                pass

    def _find_config_table(self, cursor):
        placeholders = ", ".join(["%s"] * len(CONFIG_FIELDS))
        cursor.execute(
            f"""
            SELECT table_name
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
              AND column_name IN ({placeholders})
            GROUP BY table_name
            HAVING COUNT(DISTINCT column_name) = %s
            LIMIT 1
            """,
            (*CONFIG_FIELDS, len(CONFIG_FIELDS)),
        )
        result = cursor.fetchone()
        return result["table_name"] if result else None

    def _normalise_value(self, value):
        if isinstance(value, Decimal):
            if value == value.to_integral_value():
                return int(value)
            return float(value)
        return value


class SimulationConfigCache:
    def __init__(self, db):
        self.db = db
        self._cache = {}

    def get(self, simulation_id):
        if simulation_id is None:
            return None
        if simulation_id not in self._cache:
            self._cache[simulation_id] = self.db["simulation_configs"].find_one(
                {"_id": simulation_id}
            )
        return self._cache[simulation_id]
