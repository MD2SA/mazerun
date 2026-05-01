import json
from common import constants

class ActuatorService:
    def __init__(self, mqtt_client):
        """
        :param mqtt_client: An object with a 'client' attribute (paho.mqtt.client)
        """
        self.mqtt_client = mqtt_client
        self.topic = constants.ACTUATOR_TOPIC

    def send_score(self, player, room):
        payload = {"Type": "Score", "Player": player, "Room": room}
        self._publish(payload)

    def open_door(self, player, origin, destiny):
        payload = {"Type": "OpenDoor", "Player": player, "RoomOrigin": origin, "RoomDestiny": destiny}
        self._publish(payload)

    def close_door(self, player, origin, destiny):
        payload = {"Type": "CloseDoor", "Player": player, "RoomOrigin": origin, "RoomDestiny": destiny}
        self._publish(payload)

    def close_all_doors(self, player):
        payload = {"Type": "CloseAllDoor", "Player": player}
        self._publish(payload)

    def open_all_doors(self, player):
        payload = {"Type": "OpenAllDoor", "Player": player}
        self._publish(payload)

    def _publish(self, payload):
        print(f"[Actuator] Publishing to {self.topic}: {payload}")
        self.mqtt_client.client.publish(self.topic, json.dumps(payload))
