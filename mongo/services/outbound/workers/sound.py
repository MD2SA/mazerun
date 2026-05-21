import json
import pandas as pd
from datetime import timedelta
from .base import BaseWorker
from common import constants
from common.simulation_config import SimulationConfigCache
from services.outbound.actuators import ActuatorService

class SoundWorker(BaseWorker):
    def __init__(self, queue, db, mqtt_client):
        super().__init__(queue, db, mqtt_client, "sound")
        self.player_state = {}
        self.delta_t_seconds = constants.TEMP_ANTI_SPAM_SECONDS # Reuse global constant
        self.last_alert_time = {}
        self.actuator = ActuatorService(mqtt_client)
        self.config_cache = SimulationConfigCache(db)

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
        simulation_id = doc.get("simulation_id")

        ten_secs_ago = timestamp - timedelta(seconds=constants.SOUND_MOVEMENT_WINDOW_SECONDS)

        movements = self.db["moves"].count_documents({
            "Player": player,
            "simulation_id": simulation_id,
            "timestamp": {"$gte": ten_secs_ago.isoformat(), "$lte": timestamp.isoformat()}
        })

        state = self.player_state.get(player, {"sound": sound, "movements": movements})
        sound_t_minus_1 = state["sound"]
        move_t_minus_1 = state["movements"]

        is_outlier = False
        outlier_reason = ""
        normal_noise, noise_tolerance = self._noise_limits_for(doc.get("simulation_id"))

        # Outlier Detection Rules
        if normal_noise is not None and noise_tolerance is not None:
            noise_delta = abs(sound - normal_noise)
            if noise_delta > noise_tolerance:
                is_outlier = True
                outlier_reason = (
                    f"Noise tolerance outlier: |{sound} - {normal_noise}| > "
                    f"{noise_tolerance}"
                )

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
            "simulation_id": doc.get("simulation_id"),
            "sound": sound,
            "room": doc.get("Room", doc.get("room", 0)),
            "movements_window": movements,
            "timestamp": timestamp.isoformat()
        }

        if is_outlier:
            doc_out["outlier_reason"] = outlier_reason
            self._publish(f"{self.topic_prefix}/sound_outlier", None, doc_out)
        else:
            self._publish(f"{self.topic_prefix}/sound", None, doc_out)

        # --- Actuator Logic ---
        # Trigger when approaching the limit (80% of tolerance) to avoid losing the game
        action_threshold = (
            normal_noise + (noise_tolerance * 0.8)
            if normal_noise is not None and noise_tolerance is not None
            else constants.ACTUATOR_SOUND_HIGH
        )
        
        if sound >= action_threshold:
            print(f"[SoundWorker] Sound approaching limit ({sound}). Closing all doors for Player {player}")
            self.actuator.close_all_doors(player, doc_out["simulation_id"])

            # Send System Alert with throttling
            current_time = pd.to_datetime(timestamp)
            last_alert = self.last_alert_time.get(player)
            if not last_alert or (current_time - last_alert).total_seconds() > self.delta_t_seconds:
                # Store System Alert in MongoDB for guaranteed delivery
                self.db["alerts"].insert_one({
                    "collection": doc_out["collection"],
                    "player": player,
                    "game": doc.get("game", 1),
                    "simulation_id": doc_out["simulation_id"],
                    "room": doc_out["room"],
                    "sensor": "sound",
                    "value": sound,
                    "alertType": "HIGH_SOUND",
                    "alert": f"High sound level detected ({sound} dB)",
                    "timestamp": doc_out["timestamp"],
                    "process_status": "pending"
                })
                self.last_alert_time[player] = current_time
        else:
            baseline = normal_noise if normal_noise is not None else (constants.ACTUATOR_SOUND_HIGH - 10)
            if sound <= baseline:
                print(f"[SoundWorker] Sound normalized ({sound}). Opening all doors for Player {player}")
                self.actuator.open_all_doors(player, doc_out["simulation_id"])
        # ----------------------

    def _publish(self, topic, raw_doc, payload):
        if raw_doc and "_id" in raw_doc:
            payload["mongo_id"] = str(raw_doc["_id"])
            payload["collection"] = "sound"
        self.mqtt_client.client.publish(topic, json.dumps(payload))

    def _noise_limits_for(self, simulation_id):
        config = self.config_cache.get(simulation_id)
        if not config:
            return None, None

        try:
            return float(config["normalnoise"]), float(config["noisevartoleration"])
        except (KeyError, TypeError, ValueError):
            return None, None
