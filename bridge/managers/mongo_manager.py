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

    def process_and_save(self, raw: dict) -> None:
        """
        Main entry point: process raw data and persist it.
        """
        data = self._parse_raw(raw)
        timestamp = self._now()

        self._save_move(data, timestamp)
        self._update_rooms(data, timestamp)

    # -------------------------
    # Parsing / Utils
    # -------------------------

    def _parse_raw(self, raw: dict) -> dict:
        """
        Extract and normalize raw payload.
        """
        return {
            "player": raw["Player"],
            "marsami": raw["Marsami"],
            "origin": raw["RoomOrigin"],     # corrigido
            "destiny": raw["RoomDestiny"],   # corrigido
            "status": raw["Status"],
        }

    def _now(self):
        return datetime.now(timezone.utc)

    # -------------------------
    # Operations on collections
    # -------------------------
    def _save_move(self, data: dict, timestamp) -> None:
        """
        Insert move document.
        """
        result = self.db["moves"].insert_one({
            "player": data["player"],
            "marsami": data["marsami"],
            "from": data["origin"],
            "to": data["destiny"],
            "status": data["status"],
            "timestamp": timestamp
        })

        print("Move saved:", result.inserted_id)

    def _update_rooms(self, data: dict, timestamp) -> None:
        """
        Update origin and destiny rooms.
        """
        operations = [
            UpdateOne(
                {"_id": data["destiny"]},
                {
                    "$set": {
                        "marsami_count": {
                            "$cond": [
                                {"$gt": ["$marsami_count", 0]},
                                {"$subtract": ["$marsami_count", 1]},
                                0
                            ]
                        },
                        "last_move": timestamp
                    }
                },
                upsert=True
            ),
            UpdateOne(
                {"_id": data["origin"]},
                {
                    "$inc": {"marsami_count": 1},
                    "$set": {"last_move": timestamp}
                },
                upsert=True
            )
        ]

        result = self.db["rooms"].bulk_write(operations)

        print("Rooms updated:", result.modified_count)
