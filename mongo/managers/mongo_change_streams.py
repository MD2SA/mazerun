import time
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
            "rooms": Queue()
        }

    def start_listening(self):
        resume_token = load_resume_token()
        print(f"[ChangeStream] Starting {'(resuming)' if resume_token else '(from now)'}")

        while True:
            try:
                # Match only inserts and updates where process_status is pending
                pipeline = [
                    {"$match": {
                        "operationType": {"$in": ["insert", "update", "replace"]},
                        "fullDocument.process_status": "pending"
                    }}
                ]
                
                # We need full_document to always be present
                with self.db.watch(pipeline=pipeline, full_document="updateLookup", resume_after=resume_token) as stream:
                    print("[ChangeStream] Listening for new pending documents...")

                    for change in stream:
                        coll = change["ns"]["coll"]
                        doc = change.get("fullDocument")

                        if not doc:
                            continue

                        # Dispatch to correct queue
                        if coll in self.queues:
                            self.queues[coll].put((change["_id"], doc))
                        else:
                            pass # Unsupported collection

                        
                        resume_token = change["_id"]
                        save_resume_token(resume_token)

            except PyMongoError as e:
                err_code = e._OperationFailure__code if hasattr(e, '_OperationFailure__code') else getattr(e, 'code', 0)
                if err_code == 40573 or "replica set" in str(e).lower():
                    print("[ChangeStream] Replica Set not enabled. Falling back to Polling.")
                    self._fallback_polling()
                else:
                    print(f"[ChangeStream] Mongo error, reconnecting: {e}")
                    time.sleep(5)
            except Exception as e:
                print(f"[ChangeStream] Unexpected error: {e}")
                time.sleep(5)

    def _fallback_polling(self):
        print("[ChangeStream] Polling started...")
        while True:
            try:
                for coll in self.queues.keys():
                    cursor = self.db[coll].find({"process_status": "pending"})
                    for doc in cursor:
                        self.queues[coll].put((doc["_id"], doc))
                time.sleep(1) # Poll every 1 second
            except Exception as e:
                print(f"[Fallback Polling] Error: {e}")
                time.sleep(5)
