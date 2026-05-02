import json
import pandas as pd
from .base import BaseWorker
from common import constants
from services.outbound.actuators import ActuatorService

class TemperatureWorker(BaseWorker):
    def __init__(self, queue, db, mqtt_client):
        super().__init__(queue, db, mqtt_client, "temperature")
        self.threshold = constants.TEMP_THRESHOLD
        self.delta_t_seconds = constants.TEMP_ANTI_SPAM_SECONDS
        self.last_alert_time = {}
        self.actuator = ActuatorService(mqtt_client)

    def process(self, doc):
        if "Temperature" not in doc or "Player" not in doc:
            self._publish_error("processed/invalid", doc, "Missing Temperature or Player")
            return

        try:
            temp = float(doc["Temperature"])
            player = int(doc["Player"])
        except ValueError:
            self._publish_error("processed/invalid", doc, "Invalid temperature format")
            return

        timestamp = doc.get("Hour") or doc.get("timestamp")

        doc_out = {
            "mongo_id": str(doc["_id"]),
            "collection": "temperature",
            "player": player,
            "game": doc.get("game", 1),
            "simulation_id": doc.get("simulation_id"),
            "temperature": temp,
            "timestamp": timestamp.isoformat() if hasattr(timestamp, "isoformat") else str(timestamp)
        }

        # 1. Standard alert logic (to processed/message)
        if temp >= self.threshold:
            current_time = pd.to_datetime(timestamp)
            last_alert = self.last_alert_time.get(player)
            if not last_alert or (current_time - last_alert).total_seconds() > self.delta_t_seconds:
                self.mqtt_client.client.publish("processed/message", json.dumps({
                    "mongo_id": doc_out["mongo_id"],
                    "collection": doc_out["collection"],
                    "player": player,
                    "game": doc.get("game", 1),
                    "value": temp,
                    "alert": f"High temperature detected ({temp})",
                    "timestamp": doc_out["timestamp"]
                }))
                self.last_alert_time[player] = current_time

        # 2. Actuator Logic: AC Control
        # Using thresholds from constants (assuming ACTUATOR_TEMP_HIGH and ACTUATOR_TEMP_LOW exist)
        if temp >= constants.ACTUATOR_TEMP_HIGH:
            print(f"[TemperatureWorker] High temp ({temp}). Turning ON AC for Player {player}")
            self.actuator.set_ac(player, 1)
        elif temp <= constants.ACTUATOR_TEMP_LOW:
            print(f"[TemperatureWorker] Low temp ({temp}). Turning OFF AC for Player {player}")
            self.actuator.set_ac(player, 0)

        # 3. Emergency Safety: Close all doors if temperature is critical
        if hasattr(constants, 'TEMP_SAFETY_LIMIT') and temp >= constants.TEMP_SAFETY_LIMIT:
            print(f"[TemperatureWorker] CRITICAL temp ({temp}). Closing all doors!")
            self.actuator.close_all_doors(player)

        self.mqtt_client.client.publish("processed/temperature", json.dumps(doc_out))

    def _publish_error(self, topic, doc, reason):
        payload = {"_id": str(doc.get("_id")), "error": reason}
        self.mqtt_client.client.publish(topic, json.dumps(payload))
