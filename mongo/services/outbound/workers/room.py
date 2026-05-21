import json
from .base import BaseWorker

class RoomWorker(BaseWorker):
    def __init__(self, queue, db, mqtt_client):
        super().__init__(queue, db, mqtt_client, "rooms")

    def process(self, doc):
        room_id = doc.get("room_id")
        sim_id = doc.get("simulation_id")

        # Deduplicate and ensure integer type to prevent double-counting due to type mismatch
        raw_ids = doc.get("current_marsamis", [])
        unique_ids = {int(mid) for mid in raw_ids if mid is not None}

        odd_count = 0
        even_count = 0
        for mid in unique_ids:
            if mid % 2 == 0:
                even_count += 1
            else:
                odd_count += 1

        doc_out = {
            "mongo_id": str(doc["_id"]),
            "collection": "rooms",
            "room": room_id,
            "game": doc.get("game", 1),
            "simulation_id": sim_id,
            "odd_marsamis": odd_count,
            "even_marsamis": even_count,
            "timestamp": doc.get("last_update").isoformat() if hasattr(doc.get("last_update"), "isoformat") else str(doc.get("last_update"))
        }

        if odd_count > 0 and odd_count == even_count:
            # Score condition met
            action_payload = {
                "command": "score",
                "game": doc.get("game", 1),
                "simulation_id": sim_id,
                "room": room_id,
                "reason": "odd_equals_even"
            }
            # Actuator topic
            self.mqtt_client.client.publish("actuator/score", json.dumps(action_payload))
            
            action_copy = action_payload.copy()
            action_copy["collection"] = doc_out["collection"]
            action_copy["simulation_id"] = sim_id
            action_copy["process_status"] = "pending"
            # In room.py, action_payload already has 'command', 'room', etc. 
            # We must set timestamp and sensor because AlertWorker expects it.
            action_copy["sensor"] = "room_score"
            action_copy["timestamp"] = doc_out["timestamp"]
            
            self.db["alerts"].insert_one(action_copy)

            doc_out["scored"] = True

        # Match persistence/main.py topic: processed/ocupation
        self.mqtt_client.client.publish(f"{self.topic_prefix}/ocupation", json.dumps(doc_out))
