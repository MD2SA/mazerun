import yaml
import json
import time
import datetime
import traceback
import paho.mqtt.client as mqtt
import mysql.connector
from mysql.connector import Error
from dateutil import parser as dateutil_parser
from pymongo import MongoClient
from bson import ObjectId

# Load YAML config
with open("config.yaml") as f:
    config = yaml.safe_load(f)

mqtt_config = config.get("mqtt", {})
mysql_config = config.get("mysql", {}).get("saving", {})
mysql_consulting_config = config.get("mysql", {}).get("consulting", {})

class PersistenceService:
    def __init__(self):
        self.db = None
        self.current_sim_id = None
        self.last_move_time = 0
        self.corridors = []

        # Strategy pattern mapping
        self.topic_handlers = {
            "processed/measure": self.handle_measure,
            "processed/invalid_measure": self.handle_invalid_measure,
            "processed/temperature": self.handle_temperature,
            "processed/sound": self.handle_sound,
            "processed/sound_outlier": self.handle_sound_outlier,
            "processed/message": self.handle_message,
            "processed/ocupation": self.handle_ocupation,
        }

        self.connect_db()
        self.connect_mongo()
        self.load_corridors()

    def connect_mongo(self):
        try:
            mongo_cfg = config.get("mongo", {})
            self.mongo_client = MongoClient(mongo_cfg.get("uri", "mongodb://localhost:27017"))
            self.mongo_db = self.mongo_client[mongo_cfg.get("db", "game")]
            print(f"[Persistence] MongoDB Connected for status updates: {mongo_cfg.get('db')}")
        except Exception as e:
            print(f"[Persistence] Error connecting to MongoDB: {e}")
            self.mongo_db = None

    def load_corridors(self):
        try:
            consulting_db = mysql.connector.connect(
                host=mysql_consulting_config.get("host", "194.210.86.10"),
                port=mysql_consulting_config.get("port", 3306),
                user=mysql_consulting_config.get("user", "aluno"),
                password=mysql_consulting_config.get("password", "aluno"),
                database=mysql_consulting_config.get("db", "maze")
            )
            cursor = consulting_db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM corridor")
            self.corridors = cursor.fetchall()
            cursor.close()
            consulting_db.close()
            print(f"[Persistence] Loaded {len(self.corridors)} corridors from consulting DB")
        except Error as e:
            print(f"[Persistence] Error connecting to consulting MySQL: {e}")

    def connect_db(self):
        try:
            self.db = mysql.connector.connect(
                host=mysql_config.get("host", "localhost"),
                port=mysql_config.get("port", 3306),
                user=mysql_config.get("user", "root"),
                password=mysql_config.get("password", "root"),
                database=mysql_config.get("db", "mazerun"),
                auth_plugin="mysql_native_password"
            )
            print("[Persistence] MySQL Connected Successfully")
        except Error as e:
            print(f"[Persistence] Error connecting to MySQL: {e}")

    def create_new_simulation(self, dt):
        if not self.db or not self.db.is_connected():
            self.connect_db()
        if not self.db: return

        try:
            cursor = self.db.cursor()
            # 25 is the hardcoded team number
            cursor.execute(
                "INSERT INTO simulation (description, team, startDate) VALUES (%s, %s, %s)",
                ("Simulation Session", 25, dt)
            )
            self.current_sim_id = cursor.lastrowid
            self.db.commit()
            cursor.close()
            print(f"[Persistence] Started NEW simulation with Auto-Increment ID: {self.current_sim_id}")
        except Error as e:
            print(f"[Persistence] Error creating new simulation: {e}")

    def call_sp(self, sp_name, args):
        if not self.db or not self.db.is_connected():
            self.connect_db()
        if not self.db: return False

        cursor = None
        try:
            cursor = self.db.cursor()
            cursor.callproc(sp_name, args)
            self.db.commit()
            return True
        except Error as e:
            print(f"[Persistence] SP Call Error ({sp_name}): {e}")
            try:
                self.db.rollback()
            except Error:
                pass
            return False
        finally:
            if cursor:
                try:
                    cursor.close()
                except Error:
                    pass

    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            timestamp_str = payload.get("timestamp") or datetime.datetime.now().isoformat()
            # Convert any timestamp format to standard SQL timestamp format
            try:
                dt = dateutil_parser.parse(str(timestamp_str)).strftime('%Y-%m-%d %H:%M:%S')
            except (ValueError, OverflowError) as e:
                print(f"[Persistence] Warning: Could not parse timestamp '{timestamp_str}', using current time. Error: {e}")
                dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            print(f"[Persistence] Received {topic}: {payload}")

            now = time.time()
            is_new_sim = False

            # Create a simulation on the very first message to satisfy foreign key constraints
            if self.current_sim_id is None:
                is_new_sim = True

            # If this is a movement, check if the maze was idle for more than 60 seconds
            elif topic == "processed/measure":
                if (now - self.last_move_time) > 60:
                    is_new_sim = True
                self.last_move_time = now

            if is_new_sim:
                self.create_new_simulation(dt)
                self.last_move_time = now

            sim_id = self.current_sim_id

            if not sim_id:
                print("[Persistence] Error: Could not acquire simulation ID, skipping message")
                return

            handler = self.topic_handlers.get(topic)
            if handler:
                success = handler(payload, dt, sim_id)
                
                # If SQL was successful, mark MongoDB document as 'done'
                mongo_id = payload.get("mongo_id")
                collection = payload.get("collection")
                
                if success:
                    if not mongo_id or not collection:
                        print(f"[Persistence] Warning: Missing mongo_id or collection in payload from {topic}. Skipping status update.")
                    elif self.mongo_db is not None:
                        try:
                            self.mongo_db[collection].update_one(
                                {"_id": ObjectId(mongo_id)},
                                {"$set": {"process_status": "done"}}
                            )
                            print(f"[Persistence] Marked {collection}/{mongo_id} as DONE in MongoDB")
                        except Exception as e:
                            print(f"[Persistence] Error updating MongoDB status for {mongo_id}: {e}")
            else:
                print(f"[Persistence] No handler registered for topic: {topic}")

        except Exception as e:
            print(f"[Persistence] Error processing message on topic '{msg.topic}': {e}")
            traceback.print_exc()

    # --- Handlers for each topic ---

    def handle_measure(self, payload, dt, sim_id):
        return self.call_sp("sp_insert_measure", (dt, payload["from"], payload["to"], payload["marsami"], payload.get("status", 1), sim_id, payload.get("mongo_id")))

    def handle_invalid_measure(self, payload, dt, sim_id):
        return self.call_sp("sp_insert_invalid_measure", (dt, payload.get("from", 0), payload.get("to", 0), payload.get("marsami", 0), 0, payload.get("error", "unknown"), sim_id, payload.get("mongo_id")))

    def handle_temperature(self, payload, dt, sim_id):
        return self.call_sp("sp_insert_temperature", (dt, float(payload["temperature"]), sim_id, payload.get("mongo_id")))

    def handle_sound(self, payload, dt, sim_id):
        return self.call_sp("sp_insert_sound", (dt, float(payload["sound"]), sim_id, payload.get("mongo_id")))

    def handle_sound_outlier(self, payload, dt, sim_id):
        return self.call_sp("sp_insert_sound_outlier", (dt, "sound", payload.get("sound", 0), payload.get("outlier_reason", ""), sim_id, payload.get("mongo_id")))

    def handle_message(self, payload, dt, sim_id):
        # Determine strict sensor values: "1" for temperature, "2" for sound
        raw_sensor = payload.get("sensor", "temperature").lower()
        sensor = "2" if raw_sensor == "sound" else "1"

        # Handle 'score' events from room_handler
        if payload.get("command") == "score":
            value = payload.get("room", 0)
            alert_type = "SCORE"
            alert = payload.get("reason", "")
        else:
            # Handle standard temperature/sensor messages
            value = payload.get("value", 0)
            alert_type = payload.get("alertType", "HIGH_TEMP")
            alert = payload.get("alert", "")
            
        return self.call_sp("sp_insert_message", (dt, sensor, value, alert_type, alert, sim_id, payload.get("mongo_id")))
    def handle_ocupation(self, payload, dt, sim_id):
        return self.call_sp("sp_update_ocupation", (payload.get("room"), payload.get("odd_marsamis", 0), payload.get("even_marsamis", 0), sim_id, payload.get("mongo_id")))

if __name__ == "__main__":
    service = PersistenceService()

    # Initialize MQTT
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.on_message = service.on_message

    broker = mqtt_config.get("broker")
    port = mqtt_config.get("port")

    print(f"[Persistence] Connecting to MQTT broker {broker}:{port}")
    client.connect(broker, port, 60)

    topics = [
        "processed/measure",
        "processed/invalid_measure",
        "processed/temperature",
        "processed/sound",
        "processed/sound_outlier",
        "processed/message",
        "processed/ocupation",
    ]

    for t in topics:
        client.subscribe(t, qos=1)
        
    print("[Persistence] Listening for processed events...")
    client.loop_forever()
