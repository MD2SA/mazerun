import threading
import json
import traceback

class BaseWorker(threading.Thread):
    def __init__(self, queue, db, mqtt_client, collection_name):
        super().__init__(daemon=True)
        self.queue = queue
        self.db = db
        self.mqtt_client = mqtt_client
        self.collection_name = collection_name
        self.collection = db[collection_name]

    def run(self):
        while True:
            try:
                change_id, doc = self.queue.get()
                doc_id = doc["_id"]
                
                # Atomic attempt to acquire document for processing
                result = self.collection.find_one_and_update(
                    {"_id": doc_id, "process_status": "pending"},
                    {"$set": {"process_status": "processing"}}
                )
                
                if result:
                    # Successfully acquired lock
                    try:
                        self.process(doc)
                        # Mark as done
                        self.collection.update_one(
                            {"_id": doc_id},
                            {"$set": {"process_status": "done"}}
                        )
                    except Exception as e:
                        print(f"[Worker:{self.collection_name}] Error processing doc {doc_id}: {e}")
                        traceback.print_exc()
                        # Could set to error or retry
                self.queue.task_done()
            except Exception as e:
                print(f"[Worker:{self.collection_name}] System error: {e}")

    def process(self, doc):
        """Override this method to implement processing logic."""
        raise NotImplementedError
