from pymongo import MongoClient, UpdateOne
from datetime import datetime, timezone

class MongoManager:

    def __init__(self, uri: str, db: str):
        self.client = MongoClient(uri)
        self.db = self.client[db]

        self.client.drop_database(db)
        print(f"[DB] Database {db} wiped for test purposes")
        print("[DB] MongoManager ready", self.db.name)

    # -------------------------
    # Public API
    # -------------------------

    def process_message(self, topic, payload):
        if "mazemov" in topic:
            self._handle_movement(payload)

        elif "mazetemp" in topic:
            self._handle_temperature(payload)

        elif "mazesound" in topic:
            self._handle_sound(payload)

    # -------------------------
    # Utils
    # -------------------------

    def _update_rooms(self, data: dict, timestamp):
        # Decreases destiny room (if exists)
        self.db["rooms"].update_one(
            {"_id": data["destiny"]},
            {
                "$inc": {"marsami_count": -1},
                "$set": {"last_move": timestamp, "process_status": "pending", "game": 1}
            },
            upsert=True
        )

        # Fix invalid values
        self.db["rooms"].update_one(
            {"_id": data["destiny"], "marsami_count": {"$lt": 0}},
            {"$set": {"marsami_count": 0}}
        )

        # Increases origin room
        self.db["rooms"].update_one(
            {"_id": data["origin"]},
            {
                "$inc": {"marsami_count": 1},
                "$set": {"last_move": timestamp, "process_status": "pending", "game": 1}
            },
            upsert=True
        )

    def _save_move(self, data: dict, timestamp):
        result = self.db["moves"].insert_one({
            "player": data["player"],
            "game": 1,
            "marsami": data["marsami"],
            "from": data["origin"],
            "to": data["destiny"],
            "status": data["status"],
            "process_status": "pending",
            "timestamp": timestamp
        })
        print("Move saved:", result.inserted_id)

    def _now(self):
        return datetime.now(timezone.utc)

    # -------------------------
    # Movement Handler
    # -------------------------

    def _handle_movement(self, raw):
        data = {
                "player": raw["Player"],
                "marsami": raw["Marsami"],
                "origin": raw["RoomOrigin"],
                "destiny": raw["RoomDestiny"],
                "status": raw["Status"]
        }

        timestamp = self._now()

        self._save_move(data, timestamp)
        self._update_rooms(data, timestamp)

    # -------------------------
    # Temperature Handler
    # -------------------------

    def _handle_temperature(self, raw):
        data = {
            "player": raw["Player"],
            "game": 1,
            "temperature": raw["Temperature"],
            "process_status": "pending",
            "timestamp": datetime.fromisoformat(raw["Hour"])
        }

        self.db["temperature"].insert_one(data)

        print("Temperature saved")

    # -------------------------
    # Sound Handler
    # -------------------------

    def _handle_sound(self, raw):
        data = {
                "player": raw["Player"],
                "game": 1,
                "sound": raw["Sound"],
                "process_status": "pending",
                "timestamp": datetime.fromisoformat(raw["Hour"])
        }

        self.db["sound"].insert_one(data)

        print("Sound saved")

