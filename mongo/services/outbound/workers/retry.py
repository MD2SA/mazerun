import threading
import time
from datetime import datetime, timezone, timedelta

class RetryWorker(threading.Thread):
    def __init__(self, db, timeout_seconds=10):
        super().__init__(daemon=True)
        self.db = db
        self.timeout_seconds = timeout_seconds
        self.collections = ["moves", "temperature", "sound", "rooms", "alerts"]

    def run(self):
        print(f"[RetryWorker] Started (timeout: {self.timeout_seconds}s)")
        while True:
            try:
                threshold = datetime.now(timezone.utc) - timedelta(seconds=self.timeout_seconds)
                
                for coll_name in self.collections:
                    coll = self.db[coll_name]
                    
                    # Find documents in 'processing' state that are older than threshold
                    # and reset them to 'pending' so the dispatcher/workers pick them up again
                    result = coll.update_many(
                        {
                            "process_status": "processing",
                            "sent_at": {"$lt": threshold}
                        },
                        {
                            "$set": {"process_status": "pending"},
                            "$unset": {"sent_at": ""}
                        }
                    )
                    
                    if result.modified_count > 0:
                        print(f"[RetryWorker] Reset {result.modified_count} stale documents to 'pending' in {coll_name}")
                
                time.sleep(5) # Check every 5 seconds
            except Exception as e:
                print(f"[RetryWorker] Error: {e}")
                time.sleep(10)
