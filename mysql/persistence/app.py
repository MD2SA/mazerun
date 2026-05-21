import json
import ast
import datetime
import traceback
import re
import paho.mqtt.client as mqtt
from dateutil import parser as dateutil_parser

from common.config_loader import load_config
from common.mysql_connection import MySQLConnection
from handlers.data_handlers import (
    MeasureHandler, InvalidMeasureHandler, TemperatureHandler,
    SoundHandler, SoundOutlierHandler, AlertHandler, OccupationHandler,
    ActionHandler
)

class PersistenceApp:
    """Main Persistence Service (The 'App Real'):
    - Listens for processed data from MongoDB via MQTT.
    - Persists data to MySQL.
    - Uses 'simulation_id' provided in the MQTT payload (stamped by MongoDB).
    - If no simulation_id is present, it falls back to SimulationManager (legacy/idle mode).
    """
    def __init__(self):
        self.config = load_config()
        self.mqtt_config = self.config.get("mqtt", {})
        mysql_config = self.config.get("mysql", {}).get("saving", {})

        self.db_manager = MySQLConnection(mysql_config)

        # Initialize handlers
        prefix = self.mqtt_config.get("internal_prefix", "processed")
        self.handlers = {
            f"{prefix}/measure": MeasureHandler(self.db_manager),
            f"{prefix}/invalid_measure": InvalidMeasureHandler(self.db_manager),
            f"{prefix}/temperature": TemperatureHandler(self.db_manager),
            f"{prefix}/sound": SoundHandler(self.db_manager),
            f"{prefix}/sound_outlier": SoundOutlierHandler(self.db_manager),
            f"{prefix}/message": AlertHandler(self.db_manager),
            f"{prefix}/ocupation": OccupationHandler(self.db_manager),
            "pisid_mazeact": ActionHandler(self.db_manager),
        }

    def decode_action_payload(self, raw_text):
        if not raw_text.startswith("{") or not raw_text.endswith("}"):
            return None

        payload = {}
        entries = raw_text[1:-1].split(",")
        for entry in entries:
            if ":" not in entry:
                return None

            key, value = entry.split(":", 1)
            key = key.strip()
            value = value.strip()

            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
                return None

            if re.fullmatch(r"-?\d+", value):
                payload[key] = int(value)
            else:
                payload[key] = value.strip("\"'")

        return payload

    def decode_payload(self, topic, raw_payload):
        raw_text = raw_payload.decode(errors="replace")

        try:
            payload = json.loads(raw_text)
        except json.JSONDecodeError:
            try:
                payload = ast.literal_eval(raw_text)
            except (SyntaxError, ValueError):
                if topic == "pisid_mazeact":
                    payload = self.decode_action_payload(raw_text)
                    if payload is None:
                        print(f"[App WARNING] Ignoring invalid action payload on {topic}: {raw_text[:200]}")
                        return None
                else:
                    print(f"[App WARNING] Ignoring invalid payload on {topic}: {raw_text[:200]}")
                    return None
            else:
                print(f"[App WARNING] Accepted non-JSON payload on {topic}; publisher should use json.dumps().")

        if not isinstance(payload, dict):
            print(f"[App WARNING] Ignoring non-object payload on {topic}: {raw_text[:200]}")
            return None

        return payload

    def find_latest_simulation_id(self, player_id):
        if player_id is None:
            return None

        if not self.db_manager.is_connected():
            if not self.db_manager.connect():
                return None

        cursor = None
        try:
            cursor = self.db_manager.db.cursor()
            cursor.execute(
                "SELECT id FROM simulation WHERE player_id = %s AND team = %s ORDER BY id DESC LIMIT 1",
                (int(player_id), self.config.get("team_id", 25)),
            )
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            print(f"[App ERROR] Could not resolve simulation for player {player_id}: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = self.decode_payload(topic, msg.payload)
            if payload is None:
                return

            # 1. Parse Timestamp
            timestamp_str = payload.get("timestamp") or datetime.datetime.now().isoformat()
            try:
                dt = dateutil_parser.parse(str(timestamp_str)).strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 2. Determine Simulation ID
            # Priority: ID from payload (stamped by MongoDB)
            # We ignore any message without a simulation_id to avoid stale data.
            sim_id = payload.get("simulation_id")

            if not sim_id:
                if topic == "pisid_mazeact":
                    sim_id = self.find_latest_simulation_id(payload.get("Player"))

                if not sim_id:
                    return

            # 3. Route to Handler
            handler = self.handlers.get(topic)
            if handler:
                # Add simulation_id to payload for handlers if not already there
                payload["simulation_id"] = sim_id
                handler.handle(client, payload, dt, sim_id)
            else:
                print(f"[App] No handler for topic: {topic}")

        except Exception as e:
            print(f"[App ERROR] {e}")
            traceback.print_exc()

    def run(self):
        broker = self.mqtt_config.get("broker")
        port = self.mqtt_config.get("port")

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        client.on_message = self.on_message

        print(f"[App] Starting Real Persistence Service...")
        print(f"[App] Connecting to MQTT {broker}:{port}")
        client.connect(broker, port, 60)

        for topic in self.handlers.keys():
            client.subscribe(topic)
            print(f"[App] Subscribed to {topic}")

        client.loop_forever()

if __name__ == "__main__":
    app = PersistenceApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n[App] Shutting down...")
