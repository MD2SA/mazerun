import json
import pandas as pd
from .base import BaseWorker
from common import constants
from common.simulation_config import SimulationConfigCache
from services.outbound.actuators import ActuatorService

class TemperatureWorker(BaseWorker):
    def __init__(self, queue, db, mqtt_client):
        super().__init__(queue, db, mqtt_client, "temperature")
        self.threshold = constants.TEMP_THRESHOLD
        self.delta_t_seconds = constants.TEMP_ANTI_SPAM_SECONDS
        self.last_alert_time = {}
        self.actuator = ActuatorService(mqtt_client)
        self.config_cache = SimulationConfigCache(db)

    def process(self, doc):
        if "Temperature" not in doc or "Player" not in doc:
            self._publish_error("processed/invalid", doc, "Missing Temperature or Player")
            return

        try:
            temp = float(doc["Temperature"])
            player = int(doc["Player"])
        except ValueError:
            self._publish_error("processed/invalid", doc, "Invalid temperature format")
            return

        timestamp = doc.get("Hour") or doc.get("timestamp")

        doc_out = {
            "mongo_id": str(doc["_id"]),
            "collection": "temperature",
            "player": player,
            "game": doc.get("game", 1),
            "simulation_id": doc.get("simulation_id"),
            "temperature": temp,
            "timestamp": timestamp.isoformat() if hasattr(timestamp, "isoformat") else str(timestamp)
        }

        high_threshold, low_threshold = self._thresholds_for(doc.get("simulation_id"))

        # 1. Standard alert logic (to processed/message)
        if temp >= high_threshold:
            current_time = pd.to_datetime(timestamp)
            last_alert = self.last_alert_time.get(player)
            if not last_alert or (current_time - last_alert).total_seconds() > self.delta_t_seconds:
                self.mqtt_client.client.publish(f"{self.topic_prefix}/message", json.dumps({
                    "mongo_id": f"{doc_out['mongo_id']}_alert",
                    "collection": doc_out["collection"],
                    "player": player,
                    "game": doc.get("game", 1),
                    "simulation_id": doc_out["simulation_id"],
                    "value": temp,
                    "alert": f"High temperature detected ({temp})",
                    "timestamp": doc_out["timestamp"]
                }))
                self.last_alert_time[player] = current_time

        # 2. Actuator Logic: AC Control
        if temp >= high_threshold:
            print(f"[TemperatureWorker] High temp ({temp}). Turning ON AC for Player {player}")
            self.actuator.ac_on(player)

            # Send System Alert for high temp if above threshold
            self.mqtt_client.client.publish(f"{self.topic_prefix}/message", json.dumps({
                "mongo_id": f"{doc_out['mongo_id']}_high_alert",
                "collection": doc_out["collection"],
                "player": player,
                "game": doc.get("game", 1),
                "simulation_id": doc_out["simulation_id"],
                "sensor": "temperature",
                "value": temp,
                "alertType": "HIGH_TEMP",
                "alert": f"High temperature detected ({temp}°C). AC ON.",
                "timestamp": doc_out["timestamp"]
            }))

        elif temp <= low_threshold:
            print(f"[TemperatureWorker] Low temp ({temp}). Turning OFF AC for Player {player}")
            self.actuator.ac_off(player)

            # Send System Alert for low temp
            self.mqtt_client.client.publish(f"{self.topic_prefix}/message", json.dumps({
                "mongo_id": f"{doc_out['mongo_id']}_low_alert",
                "collection": doc_out["collection"],
                "player": player,
                "game": doc.get("game", 1),
                "simulation_id": doc_out["simulation_id"],
                "sensor": "temperature",
                "value": temp,
                "alertType": "LOW_TEMP",
                "alert": f"Low temperature detected ({temp}°C). AC OFF.",
                "timestamp": doc_out["timestamp"]
            }))

        # 3. Emergency Safety: Close all doors if temperature is critical
        if hasattr(constants, 'TEMP_SAFETY_LIMIT') and temp >= constants.TEMP_SAFETY_LIMIT:
            print(f"[TemperatureWorker] CRITICAL temp ({temp}). Closing all doors!")
            self.actuator.close_all_doors(player)

        self.mqtt_client.client.publish(f"{self.topic_prefix}/temperature", json.dumps(doc_out))

    def _publish_error(self, topic, doc, reason):
        payload = {"_id": str(doc.get("_id")), "error": reason}
        self.mqtt_client.client.publish(topic, json.dumps(payload))

    def _thresholds_for(self, simulation_id):
        config = self.config_cache.get(simulation_id)
        if not config:
            return constants.ACTUATOR_TEMP_HIGH, constants.ACTUATOR_TEMP_LOW

        try:
            normal = float(config["normaltemperature"])
            high_tolerance = float(config["temperaturevarhightoleration"])
            low_tolerance = float(config["temperaturevarlowtoleration"])
            # Actuate when approaching the limit (80% of tolerance) to prevent losing
            margin = 0.8
            return normal + (high_tolerance * margin), normal - (low_tolerance * margin)
        except (KeyError, TypeError, ValueError):
            return constants.ACTUATOR_TEMP_HIGH, constants.ACTUATOR_TEMP_LOW
