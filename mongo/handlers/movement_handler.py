import json
from .base_handler import BaseWorker

class MovementWorker(BaseWorker):
    def __init__(self, queue, db, mqtt_client, mysql_manager):
        super().__init__(queue, db, mqtt_client, "moves")
        self.mysql_manager = mysql_manager

    def process(self, doc):
        # Raw fields: Player, RoomOrigin, RoomDestiny, Marsami
        required_fields = ["Player", "RoomOrigin", "RoomDestiny", "Marsami"]

        # 1. Validate missing fields
        missing = [f for f in required_fields if f not in doc]
        if missing:
            self._publish_invalid(doc, f"Missing fields: {missing}")
            return

        # 2. Validate types
        try:
            player = int(doc["Player"])
            origin = int(doc["RoomOrigin"])
            destiny = int(doc["RoomDestiny"])
            marsami = int(doc["Marsami"])
        except ValueError:
            self._publish_invalid(doc, "Invalid types, expected integers")
            return

        # 3. Validate logical move against MySQL
        is_valid = self.mysql_manager.is_valid_move(origin, destiny)

        doc_out = {
            "mongo_id": str(doc["_id"]),
            "collection": "moves",
            "player": player,
            "game": doc.get("game", 1), # Default to 1 if not present
            "from": origin,
            "to": destiny,
            "marsami": marsami,
            "timestamp": doc.get("Hour") or doc.get("timestamp")
        }

        # Ensure timestamp is string
        if hasattr(doc_out["timestamp"], "isoformat"):
            doc_out["timestamp"] = doc_out["timestamp"].isoformat()
        else:
            doc_out["timestamp"] = str(doc_out["timestamp"])

        if is_valid:
            # Match persistence/main.py expected topic: processed/measure
            self.mqtt_client.client.publish("processed/measure", json.dumps(doc_out))
        else:
            doc_out["error"] = "Invalid room transition"
            self.mqtt_client.client.publish("processed/invalid_measure", json.dumps(doc_out))

    def _publish_invalid(self, doc, reason):
        payload = {
            "mongo_id": str(doc["_id"]),
            "collection": "moves",
            "error": reason
        }
        if "RoomOrigin" in doc: payload["from"] = doc["RoomOrigin"]
        if "RoomDestiny" in doc: payload["to"] = doc["RoomDestiny"]
        # Match persistence/main.py expected topic: processed/invalid_measure
        self.mqtt_client.client.publish("processed/invalid_measure", json.dumps(payload))
