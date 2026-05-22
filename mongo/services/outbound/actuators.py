import json
import time
from collections import defaultdict
from common import constants

class ActuatorService:
    """Service to send actuator commands over MQTT with simple rate limiting.

    Rate limits are defined per (player, action, optional identifier) and use a sliding
    window measured in seconds. The `_action_history` dictionary maps a composite key to a
    list of timestamps (epoch seconds). Old entries are pruned on each check.
    """

    # In‑memory action history: {(player, action, identifier) -> [timestamps]}
    _action_history = defaultdict(list)

    def __init__(self, mqtt_client):
        """Create the service.

        Args:
            mqtt_client: An object exposing a `client` attribute compatible with
                `paho.mqtt.client` (has a `.publish(topic, payload)` method).
        """
        self.mqtt_client = mqtt_client
        self.topic = constants.ACTUATOR_TOPIC

    # ---------------------------------------------------------------------
    # Helper: rate limiting
    # ---------------------------------------------------------------------
    def _allow(self, player: int, action: str, simulation_id: int, limit: int, identifier: str = "") -> bool:
        """Return ``True`` if the action is allowed for the player in the given simulation.

        The key includes the simulation identifier so limits are scoped per simulation.
        No time window is enforced – the count persists for the lifetime of the process.
        """
        key = (player, action, simulation_id, identifier)
        # Initialize count if not present
        count = self._action_history.get(key, 0)
        if count >= limit:
            return False
        self._action_history[key] = count + 1
        return True

    # ---------------------------------------------------------------------
    # Private utility methods
    # ---------------------------------------------------------------------
    def _add_simulation_id(self, payload: dict, simulation_id):
        if simulation_id is not None:
            payload["simulation_id"] = simulation_id

    def _publish(self, payload: dict):
        print(f"[Actuator] Publishing to {self.topic}: {payload}")
        self.mqtt_client.client.publish(self.topic, json.dumps(payload))

    # ---------------------------------------------------------------------
    # Public actuator methods – each uses rate limiting as appropriate
    # ---------------------------------------------------------------------
    def send_score(self, player, room, simulation_id=None):
        payload = {"Type": "Score", "Player": player, "Room": room}
        self._add_simulation_id(payload, simulation_id)
        self._publish(payload)

    def open_door(self, player, origin, destiny, simulation_id=None):
        """Open a specific door – limit 3 opens per door per simulation."""
        corridor_id = f"{origin}-{destiny}"
        if not self._allow(player, "OpenDoor", simulation_id, limit=3, identifier=corridor_id):
            print(f"[Actuator] OpenDoor rate‑limited for player {player} on corridor {corridor_id}")
            return
        payload = {"Type": "OpenDoor", "Player": player, "RoomOrigin": origin, "RoomDestiny": destiny}
        self._add_simulation_id(payload, simulation_id)
        self._publish(payload)

    def close_door(self, player, origin, destiny, simulation_id=None):
        """Close a specific door – limit 3 closes per corridor per simulation."""
        corridor_id = f"{origin}-{destiny}"
        if not self._allow(player, "CloseDoor", simulation_id, limit=3, identifier=corridor_id):
            print(f"[Actuator] CloseDoor rate‑limited for player {player} on corridor {corridor_id}")
            return
        payload = {"Type": "CloseDoor", "Player": player, "RoomOrigin": origin, "RoomDestiny": destiny}
        self._add_simulation_id(payload, simulation_id)
        self._publish(payload)

    def close_all_doors(self, player, simulation_id=None):
        """Close all doors – limit 2 calls per minute per player."""
        if not self._allow(player, "CloseAllDoor", simulation_id, limit=2):
            print(f"[Actuator] CloseAllDoor rate‑limited for player {player}")
            return
        payload = {"Type": "CloseAllDoor", "Player": player}
        self._add_simulation_id(payload, simulation_id)
        self._publish(payload)

    def open_all_doors(self, player, simulation_id=None):
        """Open all doors – limit 2 calls per minute per player."""
        if not self._allow(player, "OpenAllDoor", simulation_id, limit=2):
            print(f"[Actuator] OpenAllDoor rate‑limited for player {player}")
            return
        payload = {"Type": "OpenAllDoor", "Player": player}
        self._add_simulation_id(payload, simulation_id)
        self._publish(payload)

    def ac_on(self, player, simulation_id=None):
        """Turn AC ON – unlimited calls per simulation."""
        payload = {"Type": "AcOn", "Player": player}
        self._add_simulation_id(payload, simulation_id)
        self._publish(payload)

    def ac_off(self, player, simulation_id=None):
        """Turn AC OFF – unlimited calls per simulation."""
        payload = {"Type": "AcOff", "Player": player}
        self._add_simulation_id(payload, simulation_id)
        self._publish(payload)

    def set_ac(self, player, state, simulation_id=None):
        """Set AC state (1 for ON, 0 for OFF)."""
        if state == 1:
            self.ac_on(player, simulation_id)
        else:
            self.ac_off(player, simulation_id)
