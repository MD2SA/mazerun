import json
import datetime
import traceback
import paho.mqtt.client as mqtt
from dateutil import parser as dateutil_parser

from common.config_loader import load_config
from common.mysql_connection import MySQLConnection
from core.simulation_manager import SimulationManager
from handlers.data_handlers import (
    MeasureHandler, InvalidMeasureHandler, TemperatureHandler,
    SoundHandler, SoundOutlierHandler, MessageHandler, OccupationHandler
)

class PersistenceApp:
    def __init__(self):
        self.config = load_config()
        self.mqtt_config = self.config.get("mqtt", {})
        mysql_config = self.config.get("mysql", {}).get("saving", {})
        
        self.db_manager = MySQLConnection(mysql_config)
        self.sim_manager = SimulationManager(self.db_manager)
        
        # Initialize handlers
        self.handlers = {
            "processed/measure": MeasureHandler(self.db_manager),
            "processed/invalid_measure": InvalidMeasureHandler(self.db_manager),
            "processed/temperature": TemperatureHandler(self.db_manager),
            "processed/sound": SoundHandler(self.db_manager),
            "processed/sound_outlier": SoundOutlierHandler(self.db_manager),
            "processed/message": MessageHandler(self.db_manager),
            "processed/ocupation": OccupationHandler(self.db_manager),
        }

    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            # 1. Parse Timestamp
            timestamp_str = payload.get("timestamp") or datetime.datetime.now().isoformat()
            try:
                dt = dateutil_parser.parse(str(timestamp_str)).strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 2. Manage Simulation Session
            sim_id = self.sim_manager.check_simulation(dt)
            if not sim_id:
                print("[App] Skipping message: No simulation ID")
                return

            # 3. Route to Handler
            handler = self.handlers.get(topic)
            if handler:
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
