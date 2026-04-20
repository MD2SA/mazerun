import mysql.connector
from mysql.connector import Error

class MySQLManager:
    def __init__(self, host, port, user, password, database):
        self.config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
            "auth_plugin": "mysql_native_password"
        }
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
        except Error as e:
            print(f"[MySQL] Error connecting to database: {e}")
            self.connection = None

    def is_connected(self):
        if self.connection and self.connection.is_connected():
            return True
        return False
        
    def ensure_connection(self):
        if not self.is_connected():
            self.connect()

    def is_valid_move(self, room_a: int, room_b: int) -> bool:
        """
        Validates if a move is valid by checking the corridor table.
        Table schema: ID; Rooma; Roomb; active; distance
        """
        self.ensure_connection()
        if not self.connection:
            return False # Fail strict or allow? If DB is down, consider invalid.

        try:
            cursor = self.connection.cursor(dictionary=True)
            # Corridor can be traversed both ways: (Rooma=A AND Roomb=B) OR (Rooma=B AND Roomb=A)
            query = """
                SELECT * FROM corridor 
                WHERE ((Rooma = %s AND Roomb = %s) OR (Rooma = %s AND Roomb = %s))
                AND active = 1
            """
            cursor.execute(query, (room_a, room_b, room_b, room_a))
            results = cursor.fetchall()
            cursor.close()
            
            return len(results) > 0
        except Error as e:
            print(f"[MySQL] Query error validation move: {e}")
            return False

    def close(self):
        if self.is_connected():
            self.connection.close()
