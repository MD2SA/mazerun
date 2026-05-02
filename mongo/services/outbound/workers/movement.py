import json
from .base import BaseWorker
from services.outbound.actuators import ActuatorService

class MovementWorker(BaseWorker):
    def __init__(self, queue, db, mqtt_client, mysql_manager):
        super().__init__(queue, db, mqtt_client, "moves")
        self.mysql_manager = mysql_manager
        self.actuator = ActuatorService(mqtt_client)
        # Tracking triggers per player and room to respect the 3-limit
        self.trigger_counts = {} 

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
            "game": doc.get("game", 1),
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
            self.mqtt_client.client.publish("processed/measure", json.dumps(doc_out))
            
            # --- Actuator Logic: Parity Check ---
            self._check_marsami_parity(destiny, player)
            # ----------------------
        else:
            doc_out["error"] = "Invalid room transition"
            self.mqtt_client.client.publish("processed/invalid_measure", json.dumps(doc_out))

    def _check_marsami_parity(self, room_id, current_player):
        """
        Checks if the number of even and odd marsamis in a room is equal.
        If equal, triggers the score sequence: Close -> Score -> Open.
        Limited to 3 times per room per player.
        """
        key = (current_player, room_id)
        if self.trigger_counts.get(key, 0) >= 3:
            return

        # Find latest position of each player
        pipeline = [
            {"$sort": {"timestamp": -1}},
            {"$group": {
                "_id": "$Player",
                "last_room": {"$first": "$RoomDestiny"},
                "marsami": {"$first": "$Marsami"}
            }},
            {"$match": {"last_room": room_id}}
        ]
        
        players_in_room = list(self.db["moves"].aggregate(pipeline))
        
        if not players_in_room:
            return

        evens = [p for p in players_in_room if p["marsami"] % 2 == 0]
        odds = [p for p in players_in_room if p["marsami"] % 2 != 0]

        if len(evens) == len(odds) and len(evens) > 0:
            print(f"[Actuator] Parity detected in room {room_id} for Player {current_player}. Sequence: Close -> Score -> Open")
            
            # Sequence to ensure balance doesn't break during scoring
            self.actuator.close_door(current_player)
            self.actuator.send_score(current_player, room_id)
            self.actuator.open_all_doors(current_player)
            
            self.trigger_counts[key] = self.trigger_counts.get(key, 0) + 1

    def _publish_invalid(self, doc, reason):
        payload = {
            "mongo_id": str(doc["_id"]),
            "collection": "moves",
            "error": reason
        }
        if "RoomOrigin" in doc: payload["from"] = doc["RoomOrigin"]
        if "RoomDestiny" in doc: payload["to"] = doc["RoomDestiny"]
        self.mqtt_client.client.publish("processed/invalid_measure", json.dumps(payload))
