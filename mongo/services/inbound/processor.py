import json
from datetime import datetime, timezone
from dateutil import parser as dateutil_parser


class InboundProcessor:
    """Processes inbound MQTT messages:
    - game/start  → registers active session (player_id + simulation_id) in
                    MongoDB and publishes game/start/ack to confirm receipt.
    - sensor data → saves raw document to the appropriate collection, stamped
                    with the current active session (player_id + simulation_id).

    The active session is stored in the 'active_sessions' collection (one doc
    per player_id) and in memory for fast access.
    Old pending documents for the same player are *not* re-tagged; the new
    session only applies to documents inserted after the game/start event.
    """

    def __init__(self, db, mqtt_publisher=None, team_id=25, simulation_configs=None):
        self.db = db
        # mqtt_publisher must expose .publish(topic, payload) for the ACK
        self.mqtt_publisher = mqtt_publisher
        self.team_id = team_id
        self.simulation_configs = simulation_configs

        # In-memory cache: player_id (int) → {"player_id": …, "simulation_id": …}
        self._active_sessions: dict = {}

        # Restore any previously stored active sessions from MongoDB on startup
        self._restore_sessions()

        # Start background thread to check for session termination criteria
        import threading
        self._termination_thread = threading.Thread(target=self._monitor_sessions, daemon=True)
        self._termination_thread.start()

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def _restore_sessions(self):
        """Reload active session state from MongoDB on process restart."""
        try:
            for doc in self.db["active_sessions"].find():
                pid = doc.get("_id")  # Using _id as the primary identifier
                if pid is not None:
                    self._active_sessions[pid] = {
                        "player_id": pid,
                        "simulation_id": doc.get("simulation_id"),
                    }
            if self._active_sessions:
                print(
                    f"[Inbound] Restored {len(self._active_sessions)} active "
                    "session(s) from MongoDB."
                )
        except Exception as e:
            print(f"[Inbound ERROR] Restoring sessions: {e}")

    def _register_session(self, player_id, simulation_id):
        """Store/overwrite the active session for a player in memory and MongoDB."""
        session = {"player_id": player_id, "simulation_id": simulation_id}

        # Update in-memory cache
        self._active_sessions[player_id] = session

        # Upsert into MongoDB 'active_sessions' collection with retries
        import time
        for i in range(5):
            try:
                self.db["active_sessions"].update_one(
                    {"_id": player_id},  # player_id is now the _id
                    {
                        "$set": {
                            "simulation_id": simulation_id,
                            "registered_at": datetime.now(timezone.utc),
                        }
                    },
                    upsert=True,
                )
                print(
                    f"[Inbound] ✔ Active session stored in MongoDB: "
                    f"player_id={player_id} → simulation_id={simulation_id}"
                )
                return True
            except Exception as e:
                print(f"[Inbound WARNING] Storing active session (Attempt {i+1}/5): {e}")
                time.sleep(2)
        return False

    def _get_session_for_player(self, player_id):
        """Returns the active session dict for a player, or None."""
        return self._active_sessions.get(player_id)

    def _terminate_session(self, player_id, simulation_id, reason="unknown"):
        """Terminate the active session by removing it from cache and MongoDB."""
        print(f"[Inbound] ⏹ Terminating active session: player_id={player_id}, simulation_id={simulation_id} (Reason: {reason})")
        # Remove from memory cache
        cached = self._active_sessions.get(player_id)
        if cached and cached.get("simulation_id") not in (None, simulation_id):
            print(
                f"[Inbound] Skipping cache removal for player_id={player_id}: "
                f"active simulation changed to {cached.get('simulation_id')}"
            )
        else:
            self._active_sessions.pop(player_id, None)
        
        # Delete from MongoDB active_sessions collection
        try:
            res = self.db["active_sessions"].delete_one(
                {"_id": player_id, "simulation_id": simulation_id}
            )
            if res.deleted_count > 0:
                print(f"[Inbound] ✔ Deleted active session from MongoDB for player_id={player_id}")
            else:
                print(
                    f"[Inbound] ℹ Session already absent or replaced for "
                    f"player_id={player_id}, simulation_id={simulation_id}"
                )
        except Exception as e:
            print(f"[Inbound ERROR] Deleting active session from MongoDB: {e}")

    def _monitor_sessions(self):
        """Periodically runs background checks for session termination criteria."""
        import time
        
        print("[Inbound] Session termination monitoring background thread started.")
        while True:
            try:
                # 1. Retrieve all current active sessions from MongoDB
                # (to ensure alignment across restarts/multiple instances)
                active_sessions = list(self.db["active_sessions"].find())
                
                for doc in active_sessions:
                    player_id = doc.get("_id")
                    simulation_id = doc.get("simulation_id")
                    registered_at = doc.get("registered_at")
                    
                    if player_id is None or simulation_id is None:
                        continue
                        
                    # Check Criterion 1: Timeout of 5 minutes (300 seconds)
                    if registered_at:
                        if registered_at.tzinfo is None:
                            registered_at = registered_at.replace(tzinfo=timezone.utc)
                        elapsed = (datetime.now(timezone.utc) - registered_at).total_seconds()
                        if elapsed > 300:
                            self._terminate_session(player_id, simulation_id, f"5-minute timeout reached ({int(elapsed)}s)")
                            continue
                            
                    # Check Criterion 2: All Marsamis Tired (status == 2)
                    # Get simulation configuration to know how many marsamis exist
                    total_marsamis = None
                    if self.simulation_configs:
                        config = self.simulation_configs.get_or_fetch(simulation_id)
                        if config:
                            try:
                                total_marsamis = int(config.get("numbermarsamis"))
                            except (TypeError, ValueError):
                                pass
                                
                    # Fetch the latest movement status of each Marsami in this simulation
                    pipeline = [
                        {"$match": {"simulation_id": simulation_id}},
                        {"$sort": {"timestamp": -1}},
                        {"$group": {
                            "_id": "$Marsami",
                            "latest_status": {"$first": "$Status"},
                            "latest_status_lower": {"$first": "$status"}
                        }}
                    ]
                    results = list(self.db["moves"].aggregate(pipeline))
                    
                    tired_count = 0
                    marsamis_seen = len(results)
                    for r in results:
                        st = r.get("latest_status")
                        if st is None:
                            st = r.get("latest_status_lower")
                        try:
                            st = int(st)
                        except (TypeError, ValueError):
                            st = 1
                        if st == 2:
                            tired_count += 1
                            
                    # Check if all have status == 2
                    is_all_tired = False
                    if total_marsamis is not None:
                        if marsamis_seen >= total_marsamis and tired_count >= total_marsamis:
                            is_all_tired = True
                    else:
                        if marsamis_seen > 0 and tired_count == marsamis_seen:
                            is_all_tired = True
                            
                    if is_all_tired:
                        self._terminate_session(player_id, simulation_id, "all marsamis are tired (status == 2)")
                        continue
                        
                time.sleep(5)
            except Exception as e:
                print(f"[Inbound monitor ERROR] {e}")
                time.sleep(5)

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def process_message(self, topic, payload):
        # ── team-specific game/start: register session and ACK ────────────
        topic_start = f"pisid/{self.team_id}/game/start"
        if topic == topic_start or topic == "game/start":
            self._handle_game_start(payload)
            return
        if topic == f"pisid/{self.team_id}/simulation/finished" or topic == "simulation/finished":
            self._handle_simulation_finished(payload)
            return

        # Determine target collection based on topic
        collection_name = None
        if "mazesound" in topic:
            collection_name = "sound"
        elif "mazetemp" in topic:
            collection_name = "temperature"
        elif "mazemov" in topic:
            collection_name = "moves"
        elif "mazeact" in topic:
            collection_name = "actions"

        if collection_name:
            self._save_sensor_document(collection_name, payload)

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _handle_game_start(self, payload):
        """Register active session and publish ACK back to MySQL/persistence."""
        if isinstance(payload, dict):
            player_id = payload.get("player_id")
            try:
                if player_id is not None:
                    player_id = int(player_id)
            except: pass
            simulation_id = payload.get("simulation_id")
            handshake_id = payload.get("handshake_id")
            number_marsamis = payload.get("numbermarsamis")
        elif isinstance(payload, int):
            print(f"[Inbound WARNING] game/start received raw integer: {payload}. Missing simulation_id.")
            player_id = payload
            simulation_id = None
            handshake_id = None
            number_marsamis = None
        else:
            print(f"[Inbound ERROR] game/start received invalid payload: {payload} (Type: {type(payload)})")
            return

        if player_id is None or simulation_id is None:
            print(
                f"[Inbound ERROR] game/start received with missing fields: {payload}"
            )
            return

        print(
            f"[Inbound] game/start received — player_id={player_id}, "
            f"simulation_id={simulation_id}"
        )

        if self.simulation_configs:
            # If the payload explicitly includes the number of marsamis, save it to the config repo
            if number_marsamis is not None:
                self.simulation_configs.save(simulation_id, {"numbermarsamis": number_marsamis})
                print(f"[Inbound] Saved numbermarsamis={number_marsamis} to config repo from handshake.")

            config = self.simulation_configs.get_or_fetch(simulation_id)
            if config:
                print(
                    f"[Inbound] Loaded simulation config for simulation_id={simulation_id}"
                )
            else:
                print(
                    f"[Inbound WARNING] Simulation config unavailable for "
                    f"simulation_id={simulation_id}. Workers will use defaults."
                )

        # Store session in MongoDB + in-memory
        self._register_session(player_id, simulation_id)

        # Publish ACK so that MySQL/persistence can unblock and launch mazerun.exe
        if self.mqtt_publisher:
            topic_ack = f"pisid/{self.team_id}/game/start/ack"
            ack_payload = {"player_id": player_id, "simulation_id": simulation_id}
            if handshake_id:
                ack_payload["handshake_id"] = handshake_id
            ack = json.dumps(ack_payload)
            try:
                self.mqtt_publisher.publish(topic_ack, ack)
                print(
                    f"[Inbound] ✔ Published ACK to {topic_ack} for "
                    f"player_id={player_id}, simulation_id={simulation_id}"
                )
            except Exception as e:
                print(f"[Inbound ERROR] Publishing game/start/ack: {e}")
        else:
            print(
                "[Inbound WARNING] No mqtt_publisher set — cannot send "
                "game/start/ack. mazerun.exe will not start."
            )

    def _handle_simulation_finished(self, payload):
        """Terminate active session from MQTT event published by /mysql."""
        if not isinstance(payload, dict):
            print(f"[Inbound WARNING] simulation/finished invalid payload type: {type(payload)}")
            return

        try:
            player_id = int(payload.get("player_id"))
            simulation_id = int(payload.get("simulation_id"))
        except (TypeError, ValueError):
            print(f"[Inbound WARNING] simulation/finished missing fields: {payload}")
            return

        self._terminate_session(
            player_id,
            simulation_id,
            reason="mazerun.exe process terminated (MQTT simulation/finished)"
        )

    def _save_sensor_document(self, collection_name, payload):
        """Save a raw sensor document to MongoDB, stamped with active session."""
        # 1. Build the document
        doc = payload.copy() if isinstance(payload, dict) else {"data": payload}
        doc["process_status"] = "pending"

        # Standardise timestamp
        raw_ts = doc.get("Hour") or doc.get("timestamp")
        if raw_ts:
            try:
                dt = dateutil_parser.parse(str(raw_ts))
                doc["timestamp"] = dt.isoformat()
            except Exception:
                doc["timestamp"] = datetime.now(timezone.utc).isoformat()
        else:
            doc["timestamp"] = datetime.now(timezone.utc).isoformat()

        if "Hour" in doc:
            del doc["Hour"]

        # 2. Stamp with active session (player_id + simulation_id)
        player_id = doc.get("Player") or doc.get("player_id")
        if player_id is not None:
            try:
                player_id = int(player_id)
            except (ValueError, TypeError):
                player_id = None

        session = self._get_session_for_player(player_id) if player_id is not None else None

        if session:
            doc["player_id"] = session["player_id"]
            doc["simulation_id"] = session["simulation_id"]
        else:
            doc["player_id"] = player_id
            doc["simulation_id"] = None
            self.db["discarded_events"].insert_one({
                "collection": collection_name,
                "payload": doc,
                "reason": "no_active_session",
                "player_id": player_id,
                "discarded_at": datetime.now(timezone.utc),
            })
            if player_id is not None:
                print(
                    f"[Inbound WARNING] Discarded '{collection_name}' event: "
                    f"no active session for player_id={player_id}."
                )
            else:
                print(
                    f"[Inbound WARNING] Discarded '{collection_name}' event: "
                    "missing/invalid player_id."
                )
            return

        # 3. Persist
        self.db[collection_name].insert_one(doc)
        print(
            f"[Inbound] Saved to '{collection_name}' — "
            f"player_id={doc.get('player_id')}, "
            f"simulation_id={doc.get('simulation_id')}"
        )

        # 4. Stateful index update for movement documents
        if collection_name == "moves":
            self._update_rooms(payload, doc.get("simulation_id"), doc.get("player_id"))

    def _update_rooms(self, raw, simulation_id, player_id):
        if not isinstance(raw, dict):
            return

        # Ensure consistent types to avoid duplicates in current_marsamis sets
        try:
            origin = int(raw.get("RoomOrigin")) if raw.get("RoomOrigin") is not None else None
            destiny = int(raw.get("RoomDestiny")) if raw.get("RoomDestiny") is not None else None
            marsami_id = int(raw.get("Marsami")) if raw.get("Marsami") is not None else None
        except (ValueError, TypeError):
            return

        if marsami_id is None:
            return

        # --- Self-Healing Logic ---
        # Ensure a marsami is removed from any OTHER room (1-10) before adding to destiny.
        # This prevents a marsami from being counted twice if messages arrive out of order.
        # We exclude Room 0 from this automatic removal to keep it as a static reference
        # as per user preference (Room 0 = 30 marsamis).
        self.db["rooms"].update_many(
            {
                "simulation_id": simulation_id,
                "room_id": {"$nin": [0, destiny]},
                "current_marsamis": marsami_id
            },
            {
                "$pull": {"current_marsamis": marsami_id},
                "$set": {
                    "process_status": "pending",
                    "last_update": datetime.now(timezone.utc),
                },
            }
        )

        # 1. ADD to destiny room
        if destiny is not None:
            self.db["rooms"].update_one(
                {"room_id": destiny, "simulation_id": simulation_id},
                {
                    "$inc": {"marsami_count": 1},
                    "$addToSet": {"current_marsamis": marsami_id},
                    "$set": {
                        "player_id": player_id,
                        "process_status": "pending",
                        "last_update": datetime.now(timezone.utc),
                    },
                },
                upsert=True,
            )

        # 2. REMOVE from origin (Manual pull)
        # We only pull from origin if it's not Room 0 and not the same as destiny.
        if origin is not None and origin != 0 and origin != destiny:
            self.db["rooms"].update_one(
                {"room_id": origin, "simulation_id": simulation_id},
                {
                    "$inc": {"marsami_count": -1},
                    "$pull": {"current_marsamis": marsami_id},
                    "$set": {
                        "process_status": "pending",
                        "last_update": datetime.now(timezone.utc),
                    },
                },
            )
