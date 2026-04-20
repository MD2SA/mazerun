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
        if "temperature" not in doc or "player" not in doc:
            self._publish_error("processed/invalid", doc, "Missing temperature or player")
            return

        # Validate type
        try:
            temp = float(doc["temperature"])
            player = int(doc["player"])
        except ValueError:
            self._publish_error("processed/invalid", doc, "Invalid temperature format")
            return
            
        doc_out = {
            "player": player,
            "game": doc.get("game", 1),
            "temperature": temp,
            "timestamp": doc.get("timestamp").isoformat() if hasattr(doc.get("timestamp"), "isoformat") else str(doc.get("timestamp"))
        }

        # Check threshold
        if temp >= self.threshold:
            current_time = pd.to_datetime(doc.get("timestamp"))
            
            # Anti-spam window
            last_alert = self.last_alert_time.get(player)
            if not last_alert or (current_time - last_alert).total_seconds() > self.delta_t_seconds:
                # Generate Alert
                self.mqtt_client.client.publish("processed/alerts", json.dumps({
                    "player": player,
                    "game": doc.get("game", 1),
                    "alert": f"High temperature detected ({temp})",
                    "timestamp": doc_out["timestamp"]
                }))
                self.last_alert_time[player] = current_time

        # Always publish valid temperature if format is OK
        self.mqtt_client.client.publish("processed/temperature", json.dumps(doc_out))

    def _publish_error(self, topic, doc, reason):
        payload = {"_id": str(doc.get("_id")), "error": reason}
        self.mqtt_client.client.publish(topic, json.dumps(payload))
