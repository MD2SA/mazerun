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
        if "sound" not in doc or "player" not in doc:
            self._publish("processed/invalid", doc, {"error": "Missing fields"})
            return

        try:
            sound = float(doc["sound"])
            player = int(doc["player"])
        except ValueError:
            self._publish("processed/invalid", doc, {"error": "Invalid types"})
            return
            
        timestamp = pd.to_datetime(doc.get("timestamp")).to_pydatetime()

        # Query movements for the player in the last X seconds
        ten_secs_ago = timestamp - timedelta(seconds=constants.SOUND_MOVEMENT_WINDOW_SECONDS)
        # Assuming moves use datetime objects for timestamp 
        movements = self.db["moves"].count_documents({
            "player": player,
            "timestamp": {"$gte": ten_secs_ago, "$lte": timestamp}
        })
        
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
            "player": player,
            "game": doc.get("game", 1),
            "sound": sound,
            "movements_window": movements,
            "timestamp": doc.get("timestamp").isoformat() if hasattr(doc.get("timestamp"), "isoformat") else str(doc.get("timestamp"))
        }

        if is_outlier:
            doc_out["outlier_reason"] = outlier_reason
            self._publish("processed/outliers", None, doc_out)
        else:
            self._publish("processed/sound", None, doc_out)

    def _publish(self, topic, raw_doc, payload):
        if raw_doc and "_id" in raw_doc:
            payload["_id"] = str(raw_doc["_id"])
        self.mqtt_client.client.publish(topic, json.dumps(payload))
