import json
import pandas as pd
import numpy as np
from datetime import timedelta
from .base_handler import BaseWorker
import constants

class SoundWorker(BaseWorker):
    def __init__(self, queue, db, mqtt_client):
        super().__init__(queue, db, mqtt_client, "sound")
        self.player_state = {}

    def process(self, doc):
        # Raw fields: Player, Sound, Hour
        if "Sound" not in doc or "Player" not in doc:
            self._publish("processed/invalid", doc, {"error": "Missing Sound or Player"})
            return

        try:
            sound = float(doc["Sound"])
            player = int(doc["Player"])
        except ValueError:
            self._publish("processed/invalid", doc, {"error": "Invalid types"})
            return
            
        timestamp_raw = doc.get("Hour") or doc.get("timestamp")
        timestamp = pd.to_datetime(timestamp_raw).to_pydatetime()

        # Query movements for the player in the last X seconds
        ten_secs_ago = timestamp - timedelta(seconds=constants.SOUND_MOVEMENT_WINDOW_SECONDS)
        
        # We will query using the standardized 'timestamp' field
        movements = self.db["moves"].count_documents({
            "Player": player,
            "timestamp": {"$gte": ten_secs_ago.isoformat(), "$lte": timestamp.isoformat()}
        })
        # If the above query is too strict with raw strings, we might need to adjust, 
        # but for now we assume it's stored in a way that allows range queries or we use the processed logic.
        
        state = self.player_state.get(player, {"sound": sound, "movements": movements})
        sound_t_minus_1 = state["sound"]
        move_t_minus_1 = state["movements"]
        
        is_outlier = False
        outlier_reason = ""
        
        # 1. Ratio
        if movements > 0:
            ratio = sound / movements
            if ratio > constants.SOUND_RATIO_MAX or ratio < constants.SOUND_RATIO_MIN:
                is_outlier = True
                outlier_reason = f"Ratio outlier: {ratio:.2f}"
                
        # 2. Temporal variation
        delta_sound = abs(sound - sound_t_minus_1)
        delta_movement = abs(movements - move_t_minus_1)
        if delta_movement <= constants.SOUND_DELTA_MOVEMENT_MAX and delta_sound > constants.SOUND_DELTA_SOUND_THRESHOLD:
            is_outlier = True
            outlier_reason = f"Temporal change outlier: dS={delta_sound}, dM={delta_movement}"
            
        # 3. Absolute diff
        if abs(sound - movements) > constants.SOUND_ABS_DIFF_THRESHOLD:
            is_outlier = True
            outlier_reason = f"Absolute diff outlier: |{sound} - {movements}| > {constants.SOUND_ABS_DIFF_THRESHOLD}"

        # Update state for next round
        self.player_state[player] = {"sound": sound, "movements": movements}

        doc_out = {
            "mongo_id": str(doc["_id"]),
            "collection": "sound",
            "player": player,
            "game": doc.get("game", 1),
            "sound": sound,
            "movements_window": movements,
            "timestamp": timestamp.isoformat()
        }

        if is_outlier:
            doc_out["outlier_reason"] = outlier_reason
            # Match persistence/main.py topic: processed/sound_outlier
            self._publish("processed/sound_outlier", None, doc_out)
        else:
            # Match persistence/main.py topic: processed/sound
            self._publish("processed/sound", None, doc_out)

    def _publish(self, topic, raw_doc, payload):
        if raw_doc and "_id" in raw_doc:
            payload["mongo_id"] = str(raw_doc["_id"])
            payload["collection"] = "sound"
        self.mqtt_client.client.publish(topic, json.dumps(payload))
