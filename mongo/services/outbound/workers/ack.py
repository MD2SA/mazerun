import json
import paho.mqtt.client as mqtt
import threading
from datetime import datetime, timezone
from bson import ObjectId

class AckWorker(threading.Thread):
    def __init__(self, broker, port, db):
        super().__init__(daemon=True)
        self.db = db

        from common.config_loader import load_config
        config = load_config()
        self.ack_topic = config.get("mqtt", {}).get("ack_topic", "persistence/ack")

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(broker, port, 60)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("[AckWorker] Connected to MQTT")
            client.subscribe(self.ack_topic)
            print(f"[AckWorker] Subscribed to {self.ack_topic}")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            mongo_id = payload.get("mongo_id")
            collection_name = payload.get("collection")
            
            if mongo_id:
                self.mark_as_processed(mongo_id, collection_name)
        except Exception as e:
            print(f"[AckWorker ERROR] {e}")

    def mark_as_processed(self, mongo_id, collection_name=None):
        # Handle derived IDs (like alerts) by stripping the suffix
        source_id = mongo_id
        if isinstance(mongo_id, str) and "_" in mongo_id:
            source_id = mongo_id.split("_")[0]

        try:
            oid = ObjectId(source_id)
        except:
            oid = source_id

        if collection_name:
            result = self.db[collection_name].update_one(
                {"_id": oid, "process_status": {"$ne": "processed"}},
                {"$set": {"process_status": "processed", "processed_at": datetime.now(timezone.utc)}}
            )
            if result.modified_count > 0:
                print(f"[AckWorker] Document {oid} in {collection_name} marked as PROCESSED (from {mongo_id})")
            return

        # Fallback search
        collections = ["moves", "temperature", "sound", "actions", "rooms", "alerts"]
        for coll in collections:
            result = self.db[coll].update_one(
                {"_id": oid, "process_status": {"$ne": "processed"}},
                {"$set": {"process_status": "processed", "processed_at": datetime.now(timezone.utc)}}
            )
            if result.modified_count > 0:
                print(f"[AckWorker] Document {mongo_id} in {coll} marked as PROCESSED (searched)")
                return

    def run(self):
        print("[AckWorker] Starting MQTT loop...")
        self.client.loop_forever()
