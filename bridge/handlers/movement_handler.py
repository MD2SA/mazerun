import json
from .base_handler import BaseWorker

class MovementWorker(BaseWorker):
    def __init__(self, queue, db, mqtt_client, mysql_manager):
        super().__init__(queue, db, mqtt_client, "moves")
        self.mysql_manager = mysql_manager

    def process(self, doc):
        required_fields = ["player", "from", "to", "marsami"]
        
        # 1. Validate missing fields
        missing = [f for f in required_fields if f not in doc]
        if missing:
            self._publish_invalid(doc, f"Missing fields: {missing}")
            return
            
        # 2. Validate types
        try:
            player = int(doc["player"])
            origin = int(doc["from"])
            destiny = int(doc["to"])
            marsami = int(doc["marsami"])
        except ValueError:
            self._publish_invalid(doc, "Invalid types, expected integers")
            return

        # 3. Validate logical move against MySQL
        is_valid = self.mysql_manager.is_valid_move(origin, destiny)
        
        doc_out = {
            "player": player,
            "game": doc.get("game", 1),
            "from": origin,
            "to": destiny,
            "marsami": marsami,
            "timestamp": doc.get("timestamp").isoformat() if hasattr(doc.get("timestamp"), "isoformat") else str(doc.get("timestamp"))
        }

        if is_valid:
            self.mqtt_client.client.publish("processed/moves", json.dumps(doc_out))
        else:
            doc_out["error"] = "Invalid room transition"
            self.mqtt_client.client.publish("processed/invalid_moves", json.dumps(doc_out))

    def _publish_invalid(self, doc, reason):
        payload = {"_id": str(doc["_id"]), "error": reason}
        if "from" in doc: payload["from"] = doc["from"]
        if "to" in doc: payload["to"] = doc["to"]
        self.mqtt_client.client.publish("processed/invalid_moves", json.dumps(payload))
