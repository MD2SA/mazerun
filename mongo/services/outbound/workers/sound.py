import json
import pandas as pd
from datetime import timedelta
from .base import BaseWorker
from common import constants
from services.outbound.actuators import ActuatorService

class SoundWorker(BaseWorker):
    def __init__(self, queue, db, mqtt_client):
        super().__init__(queue, db, mqtt_client, "sound")
        self.player_state = {}
        self.actuator = ActuatorService(mqtt_client)

    def process(self, doc):
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

        ten_secs_ago = timestamp - timedelta(seconds=constants.SOUND_MOVEMENT_WINDOW_SECONDS)

        movements = self.db["moves"].count_documents({
            "Player": player,
            "timestamp": {"$gte": ten_secs_ago.isoformat(), "$lte": timestamp.isoformat()}
        })

        state = self.player_state.get(player, {"sound": sound, "movements": movements})
        sound_t_minus_1 = state["sound"]
        move_t_minus_1 = state["movements"]

        is_outlier = False
        outlier_reason = ""

        if movements > 0:
            ratio = sound / movements
            if ratio > constants.SOUND_RATIO_MAX or ratio < constants.SOUND_RATIO_MIN:
                is_outlier = True
                outlier_reason = f"Ratio outlier: {ratio:.2f}"

        delta_sound = abs(sound - sound_t_minus_1)
        delta_movement = abs(movements - move_t_minus_1)
        if delta_movement <= constants.SOUND_DELTA_MOVEMENT_MAX and delta_sound > constants.SOUND_DELTA_SOUND_THRESHOLD:
            is_outlier = True
            outlier_reason = f"Temporal change outlier: dS={delta_sound}, dM={delta_movement}"

        if abs(sound - movements) > constants.SOUND_ABS_DIFF_THRESHOLD:
            is_outlier = True
            outlier_reason = f"Absolute diff outlier: |{sound} - {movements}| > {constants.SOUND_ABS_DIFF_THRESHOLD}"

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
            self._publish("processed/sound_outlier", None, doc_out)
        else:
            self._publish("processed/sound", None, doc_out)

        # --- Actuator Logic ---
        if sound >= constants.ACTUATOR_SOUND_HIGH:
            self.actuator.close_all_doors(player)
        # ----------------------

    def _publish(self, topic, raw_doc, payload):
        if raw_doc and "_id" in raw_doc:
            payload["mongo_id"] = str(raw_doc["_id"])
            payload["collection"] = "sound"
        self.mqtt_client.client.publish(topic, json.dumps(payload))
