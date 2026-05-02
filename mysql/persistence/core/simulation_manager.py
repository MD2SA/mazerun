import time
from mysql.connector import Error

class SimulationManager:
    """Manages the fallback simulation creation.
    Used when a message arrives without a simulation_id (legacy or idle mode).
    """

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.current_sim_id = None
        self.current_player_id = None
        self.last_activity_time = 0
        self.idle_timeout = 60  # seconds

    def check_simulation(self, timestamp_dt, player_id=None):
        """Returns the current simulation ID or creates a new one if idle."""
        now = time.time()
        is_new = False

        if self.current_sim_id is None:
            is_new = True
        elif (now - self.last_activity_time) > self.idle_timeout:
            is_new = True

        if is_new:
            self.current_sim_id = self._create_simulation(timestamp_dt, player_id)

        self.last_activity_time = now
        return self.current_sim_id

    def _create_simulation(self, dt, player_id=None):
        """Inserts a new simulation row and returns its ID."""
        if not self.db_manager.is_connected():
            if not self.db_manager.connect():
                print("[SimManager ERROR] DB not connected.")
                return None

        try:
            cursor = self.db_manager.db.cursor()
            cursor.execute(
                "INSERT INTO simulation (description, team, startDate, player_id) "
                "VALUES (%s, %s, %s, %s)",
                ("Fallback Simulation", 25, dt, player_id),
            )
            sim_id = cursor.lastrowid
            self.db_manager.db.commit()
            cursor.close()
            print(f"[SimManager] ✔ Started fallback simulation ID: {sim_id}")
            return sim_id
        except Error as e:
            print(f"[SimManager ERROR] Creating simulation: {e}")
            return None
