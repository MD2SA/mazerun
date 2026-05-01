import json
import paho.mqtt.client as mqtt
import threading
from datetime import datetime, timezone
from bson import ObjectId

class AckWorker(threading.Thread):
    def __init__(self, broker, port, db):
        super().__init__(daemon=True)
        self.db = db
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(broker, port, 60)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("[AckWorker] Connected to MQTT")
            client.subscribe("persistence/ack")
            print("[AckWorker] Subscribed to persistence/ack")

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
        try:
            oid = ObjectId(mongo_id)
        except:
            oid = mongo_id

        if collection_name:
            self.db[collection_name].update_one(
                {"_id": oid},
                {"$set": {"process_status": "processed", "processed_at": datetime.now(timezone.utc)}}
            )
            print(f"[AckWorker] Document {mongo_id} in {collection_name} marked as PROCESSED")
            return

        # Fallback search
        collections = ["moves", "temperature", "sound", "actions", "rooms"]
        for coll in collections:
            result = self.db[coll].update_one(
                {"_id": oid},
                {"$set": {"process_status": "processed", "processed_at": datetime.now(timezone.utc)}}
            )
            if result.modified_count > 0:
                print(f"[AckWorker] Document {mongo_id} in {coll} marked as PROCESSED (searched)")
                return

    def run(self):
        print("[AckWorker] Starting MQTT loop...")
        self.client.loop_forever()
