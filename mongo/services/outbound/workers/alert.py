import json
from .base import BaseWorker

class AlertWorker(BaseWorker):
    def __init__(self, queue, db, mqtt_client):
        super().__init__(queue, db, mqtt_client, "alerts")

    def process(self, doc):
        """
        Processes an alert document from the 'alerts' collection.
        Sends the alert payload to the MQTT message topic.
        """
        payload = {
            "mongo_id": str(doc["_id"]),
            "collection": doc.get("collection", "unknown"),
            "player": doc.get("player"),
            "game": doc.get("game", 1),
            "simulation_id": doc.get("simulation_id"),
            "sensor": doc.get("sensor", "unknown"),
            "value": doc.get("value", 0),
            "alertType": doc.get("alertType", "UNKNOWN"),
            "alert": doc.get("alert", ""),
            "timestamp": doc.get("timestamp"),
            # Specific for room score alerts:
            "command": doc.get("command"),
            "room": doc.get("room"),
            "reason": doc.get("reason")
        }

        # Publish the system alert message
        topic = f"{self.topic_prefix}/message"
        self.mqtt_client.client.publish(topic, json.dumps(payload))
        print(f"[AlertWorker] Sent alert {doc['_id']} ({payload['alertType']}) to {topic}")
