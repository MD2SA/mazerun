from datetime import datetime, timezone
from dateutil import parser as dateutil_parser

class InboundProcessor:
    def __init__(self, db):
        self.db = db

    def process_message(self, topic, payload):
        # Determine target collection based on topic
        collection_name = None
        if "mazesound" in topic:
            collection_name = "sound"
        elif "mazetemp" in topic:
            collection_name = "temperature"
        elif "mazemov" in topic:
            collection_name = "moves"
        elif "mazeact" in topic:
            collection_name = "actions"

        if collection_name:
            # 1. Raw Historical Record
            doc = payload.copy() if isinstance(payload, dict) else {"data": payload}
            doc["process_status"] = "pending"
            
            # Standardize timestamp
            raw_ts = doc.get("Hour") or doc.get("timestamp")
            if raw_ts:
                try:
                    dt = dateutil_parser.parse(str(raw_ts))
                    doc["timestamp"] = dt.isoformat()
                except:
                    doc["timestamp"] = datetime.now(timezone.utc).isoformat()
            else:
                doc["timestamp"] = datetime.now(timezone.utc).isoformat()
                
            if "Hour" in doc:
                del doc["Hour"]
            
            self.db[collection_name].insert_one(doc)
            print(f"[Inbound] Saved message to {collection_name}")

            # 2. Stateful Index Update (the rooms logic)
            if collection_name == "moves":
                self._update_rooms(payload)

    def _update_rooms(self, raw):
        origin = raw.get("RoomOrigin")
        destiny = raw.get("RoomDestiny")
        marsami_id = raw.get("Marsami")

        if destiny is not None:
            self.db["rooms"].update_one(
                {"_id": destiny},
                {
                    "$inc": {"marsami_count": 1},
                    "$addToSet": {"current_marsamis": marsami_id},
                    "$set": {
                        "process_status": "pending",
                        "last_update": datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )

        if origin is not None and origin != 0:
            self.db["rooms"].update_one(
                {"_id": origin},
                {
                    "$inc": {"marsami_count": -1},
                    "$pull": {"current_marsamis": marsami_id},
                    "$set": {
                        "process_status": "pending",
                        "last_update": datetime.now(timezone.utc)
                    }
                }
            )
            
            self.db["rooms"].update_one(
                {"_id": origin, "marsami_count": {"$lt": 0}},
                {"$set": {"marsami_count": 0}}
            )
