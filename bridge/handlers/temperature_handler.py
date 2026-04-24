import json
import pandas as pd
from datetime import timedelta
from .base_handler import BaseWorker
import constants

class TemperatureWorker(BaseWorker):
    def __init__(self, queue, db, mqtt_client):
        super().__init__(queue, db, mqtt_client, "temperature")
        self.threshold = constants.TEMP_THRESHOLD
        self.delta_t_seconds = constants.TEMP_ANTI_SPAM_SECONDS
        # Keep track of last alert time per player
        self.last_alert_time = {}

    def process(self, doc):
        # Raw fields: Player, Temperature, Hour
        if "Temperature" not in doc or "Player" not in doc:
            self._publish_error("processed/invalid", doc, "Missing Temperature or Player")
            return

        # Validate type
        try:
            temp = float(doc["Temperature"])
            player = int(doc["Player"])
        except ValueError:
            self._publish_error("processed/invalid", doc, "Invalid temperature format")
            return
            
        timestamp = doc.get("Hour") or doc.get("timestamp")
        
        doc_out = {
            "player": player,
            "game": doc.get("game", 1),
            "temperature": temp,
            "timestamp": timestamp.isoformat() if hasattr(timestamp, "isoformat") else str(timestamp)
        }

        # Check threshold
        if temp >= self.threshold:
            current_time = pd.to_datetime(timestamp)
            
            # Anti-spam window
            last_alert = self.last_alert_time.get(player)
            if not last_alert or (current_time - last_alert).total_seconds() > self.delta_t_seconds:
                # Generate Alert - Match persistence/main.py topic: processed/message
                self.mqtt_client.client.publish("processed/message", json.dumps({
                    "player": player,
                    "game": doc.get("game", 1),
                    "value": temp,
                    "alert": f"High temperature detected ({temp})",
                    "timestamp": doc_out["timestamp"]
                }))
                self.last_alert_time[player] = current_time

        # Always publish valid temperature - Match persistence/main.py topic: processed/temperature
        self.mqtt_client.client.publish("processed/temperature", json.dumps(doc_out))

    def _publish_error(self, topic, doc, reason):
        payload = {"_id": str(doc.get("_id")), "error": reason}
        self.mqtt_client.client.publish(topic, json.dumps(payload))
