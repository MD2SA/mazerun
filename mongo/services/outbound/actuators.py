import json
from common import constants

class ActuatorService:
    def __init__(self, mqtt_client):
        """
        :param mqtt_client: An object with a 'client' attribute (paho.mqtt.client)
        """
        self.mqtt_client = mqtt_client
        self.topic = constants.ACTUATOR_TOPIC

    def send_score(self, player, room, simulation_id=None):
        payload = {"Type": "Score", "Player": player, "Room": room}
        self._add_simulation_id(payload, simulation_id)
        self._publish(payload)

    def open_door(self, player, origin, destiny, simulation_id=None):
        payload = {"Type": "OpenDoor", "Player": player, "RoomOrigin": origin, "RoomDestiny": destiny}
        self._add_simulation_id(payload, simulation_id)
        self._publish(payload)

    def close_door(self, player, origin, destiny, simulation_id=None):
        payload = {"Type": "CloseDoor", "Player": player, "RoomOrigin": origin, "RoomDestiny": destiny}
        self._add_simulation_id(payload, simulation_id)
        self._publish(payload)

    def close_all_doors(self, player, simulation_id=None):
        payload = {"Type": "CloseAllDoor", "Player": player}
        self._add_simulation_id(payload, simulation_id)
        self._publish(payload)

    def open_all_doors(self, player, simulation_id=None):
        payload = {"Type": "OpenAllDoor", "Player": player}
        self._add_simulation_id(payload, simulation_id)
        self._publish(payload)

    def ac_on(self, player, simulation_id=None):
        """Turn AC ON for the given player"""
        payload = {"Type": "AcOn", "Player": player}
        self._add_simulation_id(payload, simulation_id)
        self._publish(payload)

    def ac_off(self, player, simulation_id=None):
        """Turn AC OFF for the given player"""
        payload = {"Type": "AcOff", "Player": player}
        self._add_simulation_id(payload, simulation_id)
        self._publish(payload)

    def set_ac(self, player, state, simulation_id=None):
        """Set AC state (1 for ON, 0 for OFF) using hardware-compatible types"""
        if state == 1:
            self.ac_on(player, simulation_id)
        else:
            self.ac_off(player, simulation_id)

    def _add_simulation_id(self, payload, simulation_id):
        if simulation_id is not None:
            payload["simulation_id"] = simulation_id

    def _publish(self, payload):
        print(f"[Actuator] Publishing to {self.topic}: {payload}")
        self.mqtt_client.client.publish(self.topic, json.dumps(payload))
