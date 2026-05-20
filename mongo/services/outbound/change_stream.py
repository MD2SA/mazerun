import time
import os
from bson.json_util import dumps, loads
import pymongo
from pymongo.errors import PyMongoError
from queue import Queue

RESUME_TOKEN_FILE = "resume_token.json"

def load_resume_token():
    try:
        with open(RESUME_TOKEN_FILE, "r") as f:
            return loads(f.read())
    except:
        return None

def save_resume_token(token):
    with open(RESUME_TOKEN_FILE, "w") as f:
        f.write(dumps(token))

def clear_resume_token():
    try:
        os.remove(RESUME_TOKEN_FILE)
    except FileNotFoundError:
        pass

class MongoChangeStreamDispatcher:
    def __init__(self, mongo_uri, db_name):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.db_name]
        
        # Queues for each type of processing
        self.queues = {
            "moves": Queue(),
            "temperature": Queue(),
            "sound": Queue(),
            "rooms": Queue(),
            "alerts": Queue()
        }

    def start_listening(self):
        resume_token = load_resume_token()
        print(f"[ChangeStream] Starting {'(resuming)' if resume_token else '(from now)'}")
        self.queue_pending_documents()

        while True:
            try:
                # Match only inserts and updates where process_status is pending
                pipeline = [
                    {"$match": {
                        "operationType": {"$in": ["insert", "update", "replace"]},
                        "fullDocument.process_status": "pending"
                    }}
                ]
                
                watch_kwargs = {"pipeline": pipeline, "full_document": "updateLookup"}
                if resume_token:
                    watch_kwargs["resume_after"] = resume_token

                with self.db.watch(**watch_kwargs) as stream:
                    print("[ChangeStream] Listening for new pending documents...")

                    for change in stream:
                        coll = change["ns"]["coll"]
                        doc = change.get("fullDocument")

                        if not doc:
                            continue

                        # Dispatch to correct queue
                        if coll in self.queues:
                            self.queues[coll].put((change["_id"], doc))
                        
                        resume_token = change["_id"]
                        save_resume_token(resume_token)

            except PyMongoError as e:
                print(f"[ChangeStream] Mongo error: {e}")
                if getattr(e, "has_error_label", lambda label: False)("NonResumableChangeStreamError") or getattr(e, "code", None) == 280:
                    print("[ChangeStream] Resume token is invalid. Clearing token and queueing pending documents.")
                    clear_resume_token()
                    resume_token = None
                    self.queue_pending_documents()
                    time.sleep(1)
                    continue

                if "replica set" in str(e).lower():
                    print("[ChangeStream] Falling back to Polling.")
                    self._fallback_polling()
                    break
                time.sleep(5)
            except Exception as e:
                print(f"[ChangeStream] Unexpected error: {e}")
                time.sleep(5)

    def queue_pending_documents(self):
        queued = 0
        for coll, queue in self.queues.items():
            cursor = self.db[coll].find({"process_status": "pending"})
            for doc in cursor:
                queue.put((doc["_id"], doc))
                queued += 1

        if queued:
            print(f"[ChangeStream] Queued {queued} pending document(s).")

    def _fallback_polling(self):
        print("[ChangeStream] Polling started...")
        queued_ids = set()
        while True:
            try:
                for coll, queue in self.queues.items():
                    # Only find documents that are still pending
                    cursor = self.db[coll].find({"process_status": "pending"})
                    for doc in cursor:
                        doc_id = str(doc["_id"])
                        if doc_id not in queued_ids:
                            queue.put((doc["_id"], doc))
                            queued_ids.add(doc_id)
                
                # Clear tracking occasionally to keep memory low
                if len(queued_ids) > 2000:
                    queued_ids.clear()

                time.sleep(2) # Poll every 2 seconds
            except Exception as e:
                print(f"[Fallback Polling] Error: {e}")
                time.sleep(5)
