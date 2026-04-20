import yaml
import json
import time
import datetime
import paho.mqtt.client as mqtt
import mysql.connector
from mysql.connector import Error

# Load YAML config
with open("../bridge/config.yaml") as f:
    config = yaml.safe_load(f)

mqtt_config = config.get("mqtt", {})
mysql_config = config.get("mysql", {}).get("saving", {})

class PersistenceService:
    def __init__(self):
        self.db = None
        self.seen_sim_ids = set()
        self.connect_db()

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

    def call_sp(self, sp_name, args):
        if not self.db or not self.db.is_connected():
            self.connect_db()
        if not self.db: return

        try:
            cursor = self.db.cursor()
            cursor.callproc(sp_name, args)
            self.db.commit()
            cursor.close()
        except Error as e:
            print(f"[Persistence] SP Call Error ({sp_name}): {e}")

    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            timestamp_str = payload.get("timestamp", datetime.datetime.now().isoformat())
            # Convert ISO to standard SQL timestamp format
            dt = datetime.datetime.fromisoformat(timestamp_str.replace("Z", "+00:00")).strftime('%Y-%m-%d %H:%M:%S')

            print(f"[Persistence] Received {topic}: {payload}")

            sim_id = payload.get("game", 1)  # Use dynamic sim ID

            if sim_id not in self.seen_sim_ids:
                # 25 is the hardcoded team number
                self.call_sp("sp_insert_simulation", (sim_id, 25, dt))
                self.seen_sim_ids.add(sim_id)

            if topic == "processed/moves":
                # p_time, p_originRoom, p_destinyRoom, p_marsami, p_status, p_simulation_id
                self.call_sp("sp_insert_move", (dt, payload["from"], payload["to"], payload["marsami"], payload.get("status", 1), sim_id))
            
            elif topic == "processed/invalid_moves":
                # p_time, p_originRoom, p_destinyRoom, p_marsami, p_status, p_reason, p_simulation_id
                self.call_sp("sp_insert_invalid_data", (dt, payload.get("from", 0), payload.get("to", 0), payload.get("marsami", 0), 0, payload.get("error", "unknown"), sim_id))

            elif topic == "processed/temperature":
                # p_time, p_temperature, p_room, p_simulation_id
                self.call_sp("sp_insert_temperature", (dt, float(payload["temperature"]), 0, sim_id))
                
            elif topic == "processed/sound":
                 # p_time, p_sound, p_room, p_simulation_id
                self.call_sp("sp_insert_sound", (dt, float(payload["sound"]), 0, sim_id))
                
            elif topic == "processed/outliers":
                # p_time, p_sensor, p_value, p_reason, p_simulation_id
                self.call_sp("sp_insert_outlier", (dt, "sound", payload.get("sound", 0), payload.get("outlier_reason", ""), sim_id))
                
            elif topic == "processed/alerts":
                # p_time, p_sensor, p_value, p_alertType, p_description, p_simulation_id
                self.call_sp("sp_insert_alert", (dt, "temperature", payload.get("value", 0), "HIGH_TEMP", payload.get("alert", ""), sim_id))
                
            elif topic == "actuator/score":
                # p_time, p_action_type, p_target, p_value, p_simulation_id
                self.call_sp("sp_register_score_event", (dt, "odd_equals_even", str(payload.get("room", 0)), 1, sim_id))

            elif topic == "processed/rooms":
                # p_room, p_odd, p_even, p_simulation_id
                self.call_sp("sp_update_ocupation", (payload.get("room"), payload.get("odd_marsamis", 0), payload.get("even_marsamis", 0), sim_id))
                
        except Exception as e:
            print(f"[Persistence] Error processing message: {e}")

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
        "processed/moves",
        "processed/invalid_moves",
        "processed/temperature",
        "processed/sound",
        "processed/outliers",
        "processed/alerts",
        "processed/rooms",
        "actuator/score"
    ]
    
    for t in topics:
        client.subscribe(t)
        
    print("[Persistence] Listening for processed events...")
    client.loop_forever()
