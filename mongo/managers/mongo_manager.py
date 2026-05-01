from pymongo import MongoClient
from datetime import datetime, timezone
from dateutil import parser as dateutil_parser

class MongoManager:

    def __init__(self, uri: str, db_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        print(f"[DB] Connected to {db_name}. Raw ingestion ready.")

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
            # 1. Raw Historical Record (The "Raw" Rule)
            # We insert the payload exactly as received, only adding process_status
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
                
            # Remove legacy 'Hour' if it exists to clean up Mongo data
            if "Hour" in doc:
                del doc["Hour"]
            
            # Use insert_one for high-speed ingestion
            self.db[collection_name].insert_one(doc)

            # 2. Stateful Index Update (the rooms logic)
            if collection_name == "moves":
                self._update_rooms(payload)

    def _update_rooms(self, raw):
        origin = raw.get("RoomOrigin")
        destiny = raw.get("RoomDestiny")
        marsami_id = raw.get("Marsami")

        # Update Destiny: Increment count and add marsami to set
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

        # Update Origin: Decrement count and pull marsami from set
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
            
            # Safety check to avoid negative occupancy counts
            self.db["rooms"].update_one(
                {"_id": origin, "marsami_count": {"$lt": 0}},
                {"$set": {"marsami_count": 0}}
            )
    def mark_as_processed(self, mongo_id, collection_name=None):
        from bson import ObjectId
        
        try:
            oid = ObjectId(mongo_id)
        except:
            oid = mongo_id

        # If collection is known, update directly
        if collection_name:
            self.db[collection_name].update_one(
                {"_id": oid},
                {"$set": {"process_status": "processed", "processed_at": datetime.now(timezone.utc)}}
            )
            print(f"[DB] Document {mongo_id} in {collection_name} marked as PROCESSED")
            return True

        # Fallback: search all collections
        collections = ["moves", "temperature", "sound", "actions", "rooms"]
        for coll in collections:
            result = self.db[coll].update_one(
                {"_id": oid},
                {"$set": {"process_status": "processed", "processed_at": datetime.now(timezone.utc)}}
            )
            if result.modified_count > 0:
                print(f"[DB] Document {mongo_id} in {coll} marked as PROCESSED (searched)")
                return True
        return False
