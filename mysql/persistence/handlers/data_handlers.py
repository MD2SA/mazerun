from .base import BaseHandler

class MeasureHandler(BaseHandler):
    def handle(self, client, payload, dt, sim_id):
        res = self.db_manager.call_sp("sp_insert_measure", (
            dt, payload["from"], payload["to"], payload["marsami"], payload.get("status", 1), sim_id
        ))
        if res == 1: self.send_ack(client, payload)

class InvalidMeasureHandler(BaseHandler):
    def handle(self, client, payload, dt, sim_id):
        res = self.db_manager.call_sp("sp_insert_invalid_measure", (
            dt, payload.get("from", 0), payload.get("to", 0), payload.get("marsami", 0), 0, payload.get("error", "unknown"), sim_id
        ))
        if res == 1: self.send_ack(client, payload)

class TemperatureHandler(BaseHandler):
    def handle(self, client, payload, dt, sim_id):
        res = self.db_manager.call_sp("sp_insert_temperature", (dt, float(payload["temperature"]), sim_id))
        if res == 1: self.send_ack(client, payload)

class SoundHandler(BaseHandler):
    def handle(self, client, payload, dt, sim_id):
        res = self.db_manager.call_sp("sp_insert_sound", (dt, float(payload["sound"]), sim_id))
        if res == 1: self.send_ack(client, payload)

class SoundOutlierHandler(BaseHandler):
    def handle(self, client, payload, dt, sim_id):
        res = self.db_manager.call_sp("sp_insert_sound_outlier", (dt, "sound", payload.get("sound", 0), payload.get("outlier_reason", ""), sim_id))
        if res == 1: self.send_ack(client, payload)

class MessageHandler(BaseHandler):
    def handle(self, client, payload, dt, sim_id):
        raw_sensor = payload.get("sensor", "temperature").lower()
        sensor = "2" if raw_sensor == "sound" else "1"

        if payload.get("command") == "score":
            value = payload.get("room", 0)
            alert_type = "SCORE"
            alert = payload.get("reason", "")
        else:
            value = payload.get("value", 0)
            alert_type = payload.get("alertType", "HIGH_TEMP")
            alert = payload.get("alert", "")

        res = self.db_manager.call_sp("sp_insert_message", (dt, sensor, value, alert_type, alert, sim_id))
        if res == 1: self.send_ack(client, payload)

class OccupationHandler(BaseHandler):
    def handle(self, client, payload, dt, sim_id):
        res = self.db_manager.call_sp("sp_update_ocupation", (payload.get("room"), payload.get("odd_marsamis", 0), payload.get("even_marsamis", 0), sim_id))
        if res == 1: self.send_ack(client, payload)
