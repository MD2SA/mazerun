import json

class BaseHandler:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def send_ack(self, client, payload):
        ack_payload = {
            "mongo_id": payload.get("mongo_id"),
            "collection": payload.get("collection"),
        }
        client.publish("persistence/ack", json.dumps(ack_payload))
        print(f"[Handler] ACK sent for mongo_id: {ack_payload.get('mongo_id')}")

    def handle(self, client, payload, dt, sim_id):
        raise NotImplementedError
