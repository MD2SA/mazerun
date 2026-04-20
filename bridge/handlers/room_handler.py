import json
from .base_handler import BaseWorker

class RoomWorker(BaseWorker):
    def __init__(self, queue, db, mqtt_client):
        super().__init__(queue, db, mqtt_client, "rooms")

    def process(self, doc):
        room_id = doc.get("_id")
        
        # Room doc processing: query odd/even marsamis in this room
        pipeline = [
            {"$match": {"to": room_id}},
            {"$group": {
                "_id": {"marsami": "$marsami"},
                "count": {"$sum": 1} # Total times marsami went to room
            }}
        ]
        
        results = list(self.db["moves"].aggregate(pipeline))
        
        odd_count = 0
        even_count = 0
        
        for r in results:
            marsami_id = r["_id"]["marsami"]
            if marsami_id % 2 == 0:
                even_count += 1
            else:
                odd_count += 1
                
        doc_out = {
            "room": room_id,
            "game": doc.get("game", 1),
            "odd_marsamis": odd_count,
            "even_marsamis": even_count,
            "last_move": doc.get("last_move").isoformat() if doc.get("last_move") else None
        }
        
        if odd_count > 0 and odd_count == even_count:
            # Score condition met
            action_payload = {
                "command": "score",
                "game": doc.get("game", 1),
                "room": room_id,
                "reason": "odd_equals_even"
            }
            self.mqtt_client.client.publish("actuator/score", json.dumps(action_payload))
            self.mqtt_client.client.publish("processed/actions", json.dumps(action_payload))
            
            doc_out["scored"] = True
        
        self.mqtt_client.client.publish("processed/rooms", json.dumps(doc_out))
