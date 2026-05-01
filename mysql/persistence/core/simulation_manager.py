import time
from mysql.connector import Error

class SimulationManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.current_sim_id = None
        self.last_activity_time = 0
        self.idle_timeout = 60 # seconds

    def check_simulation(self, timestamp_dt):
        now = time.time()
        is_new = False

        if self.current_sim_id is None:
            is_new = True
        elif (now - self.last_activity_time) > self.idle_timeout:
            is_new = True

        if is_new:
            self._create_simulation(timestamp_dt)
        
        self.last_activity_time = now
        return self.current_sim_id

    def _create_simulation(self, dt):
        if not self.db_manager.is_connected():
            if not self.db_manager.connect():
                print("[Core ERROR] Cannot create simulation: Database not connected")
                return
        
        try:
            cursor = self.db_manager.db.cursor()
            # Hardcoded team 25 as per original code
            cursor.execute(
                "INSERT INTO simulation (description, team, startDate) VALUES (%s, %s, %s)",
                ("Simulation Session", 25, dt)
            )
            self.current_sim_id = cursor.lastrowid
            self.db_manager.db.commit()
            cursor.close()
            print(f"[Core] Started NEW simulation ID: {self.current_sim_id}")
        except Error as e:
            print(f"[Core ERROR] Creating simulation: {e}")
