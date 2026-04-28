import json
from .base_handler import BaseWorker

class RoomWorker(BaseWorker):
    def __init__(self, queue, db, mqtt_client):
        super().__init__(queue, db, mqtt_client, "rooms")

    def process(self, doc):
        room_id = doc.get("_id")
        
        # Room doc processing: query odd/even marsamis in this room
        # In the raw moves collection, destiny is "RoomDestiny" and marsami is "Marsami"
        pipeline = [
            {"$match": {"RoomDestiny": room_id}},
            {"$group": {
                "_id": {"marsami": "$Marsami"},
                "count": {"$sum": 1} # Total times marsami went to room
            }}
        ]
        
        results = list(self.db["moves"].aggregate(pipeline))
        
        odd_count = 0
        even_count = 0
        
        for r in results:
            marsami_id = r["_id"]["marsami"]
            if marsami_id is not None:
                if int(marsami_id) % 2 == 0:
                    even_count += 1
                else:
                    odd_count += 1
                 
        doc_out = {
            "mongo_id": str(doc["_id"]),
            "collection": "rooms",
            "room": room_id,
            "game": doc.get("game", 1),
            "odd_marsamis": odd_count,
            "even_marsamis": even_count,
            "timestamp": doc.get("last_update").isoformat() if hasattr(doc.get("last_update"), "isoformat") else str(doc.get("last_update"))
        }
        
        if odd_count > 0 and odd_count == even_count:
            # Score condition met
            action_payload = {
                "command": "score",
                "game": doc.get("game", 1),
                "room": room_id,
                "reason": "odd_equals_even"
            }
            # Actuator topic
            self.mqtt_client.client.publish("actuator/score", json.dumps(action_payload))
            # Match persistence/main.py topic: processed/message (for actions)
            # Actually, persistence has handle_message for processed/message
            action_copy = action_payload.copy()
            action_copy["mongo_id"] = doc_out["mongo_id"]
            action_copy["collection"] = doc_out["collection"]
            self.mqtt_client.client.publish("processed/message", json.dumps(action_copy))
            
            doc_out["scored"] = True
        
        # Match persistence/main.py topic: processed/ocupation
        self.mqtt_client.client.publish("processed/ocupation", json.dumps(doc_out))

    def _publish(self, topic, raw_doc, payload):
        if raw_doc and "_id" in raw_doc:
            payload["mongo_id"] = str(raw_doc["_id"])
            payload["collection"] = "rooms"
        self.mqtt_client.client.publish(topic, json.dumps(payload))
