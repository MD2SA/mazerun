from .base import BaseHandler

class MeasureHandler(BaseHandler):
    def handle(self, client, payload, dt, sim_id):
        res = self.db_manager.call_sp("sp_insert_measure", (
            dt, payload["from"], payload["to"], payload["marsami"], payload.get("status", 1), 
            sim_id, payload.get("mongo_id")
        ))
        if res == 1: self.send_ack(client, payload)

class InvalidMeasureHandler(BaseHandler):
    def handle(self, client, payload, dt, sim_id):
        res = self.db_manager.call_sp("sp_insert_invalid_measure", (
            dt, payload.get("from", 0), payload.get("to", 0), payload.get("marsami", 0), 
            0, payload.get("error", "unknown"), sim_id, payload.get("mongo_id")
        ))
        if res == 1: self.send_ack(client, payload)

class TemperatureHandler(BaseHandler):
    def handle(self, client, payload, dt, sim_id):
        res = self.db_manager.call_sp("sp_insert_temperature", (
            dt, float(payload["temperature"]), sim_id, payload.get("mongo_id")
        ))
        if res == 1: self.send_ack(client, payload)

class SoundHandler(BaseHandler):
    def handle(self, client, payload, dt, sim_id):
        res = self.db_manager.call_sp("sp_insert_sound", (
            dt, float(payload["sound"]), sim_id, payload.get("mongo_id")
        ))
        if res == 1: self.send_ack(client, payload)

class SoundOutlierHandler(BaseHandler):
    def handle(self, client, payload, dt, sim_id):
        res = self.db_manager.call_sp("sp_insert_sound_outlier", (
            dt, "sound", payload.get("sound", 0), payload.get("outlier_reason", ""), 
            sim_id, payload.get("mongo_id")
        ))
        if res == 1: self.send_ack(client, payload)

class AlertHandler(BaseHandler):
    def handle(self, client, payload, dt, sim_id):
        # 1. Map Sensor
        raw_sensor = str(payload.get("sensor", "temperature")).lower()
        if "sound" in raw_sensor:
            sensor = "2"
        else:
            sensor = "1"

        # 2. Determine Alert Type and Value
        if payload.get("command") == "score":
            value = payload.get("room", 0)
            alert_type = "SCORE"
            alert = payload.get("reason", "Threshold reached")
        else:
            value = payload.get("value", 0)
            alert_type = payload.get("alertType", "HIGH_TEMP")
            alert = payload.get("alert", "Threshold exceeded")

        # 3. Validate against ENUMs (Program definitions)
        allowed_types = ["SCORE", "HIGH_TEMP", "LOW_TEMP", "HIGH_SOUND"]
        if alert_type not in allowed_types:
            print(f"[Handler WARNING] Unknown alertType: {alert_type}. Defaulting to HIGH_TEMP")
            alert_type = "HIGH_TEMP"

        res = self.db_manager.call_sp("sp_insert_alert", (
            dt, sensor, value, alert_type, alert, sim_id, payload.get("mongo_id")
        ))
        if res == 1: self.send_ack(client, payload)

class OccupationHandler(BaseHandler):
    def handle(self, client, payload, dt, sim_id):
        res = self.db_manager.call_sp("sp_update_ocupation", (
            payload.get("room"), payload.get("odd_marsamis", 0), payload.get("even_marsamis", 0), 
            sim_id, payload.get("mongo_id")
        ))
        if res == 1: self.send_ack(client, payload)

class ActionHandler(BaseHandler):
    def handle(self, client, payload, dt, sim_id):
        action_type = payload.get("Type", "Unknown")
        player = payload.get("Player", "Unknown")
        
        # Default values
        target = f"Player {player}"
        value = 1
        
        # Custom logic for different types
        if action_type == "Score":
            target = f"Room {payload.get('Room', '??')}"
            value = 1
        elif action_type in ["OpenDoor", "CloseDoor"]:
            origin = payload.get("RoomOrigin", "?")
            destiny = payload.get("RoomDestiny", "?")
            target = f"{origin} -> {destiny}"
        elif action_type == "SetAC":
            state = payload.get("State", 0)
            target = "Air Conditioner"
            value = state # 1 for ON, 0 for OFF
        elif action_type == "AcOn":
            target = "Air Conditioner"
            value = 1
        elif action_type == "AcOff":
            target = "Air Conditioner"
            value = 0
        elif action_type in ["CloseAllDoor", "OpenAllDoor"]:
            target = "All Corridors"
            value = 1 if "Open" in action_type else 0

        # Insert into MySQL 'action' table
        self.db_manager.call_sp("sp_insert_action", (
            dt, action_type, target, value, sim_id
        ))
