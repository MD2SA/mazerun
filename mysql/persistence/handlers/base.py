import json

class BaseHandler:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def send_ack(self, client, payload):
        from common.config_loader import load_config
        config = load_config()
        ack_topic = config.get("mqtt", {}).get("ack_topic", "persistence/ack")

        ack_payload = {
            "mongo_id": payload.get("mongo_id"),
            "collection": payload.get("collection"),
        }
        client.publish(ack_topic, json.dumps(ack_payload))
        print(f"[Handler] ACK sent for mongo_id: {ack_payload.get('mongo_id')} to {ack_topic}")

    def handle(self, client, payload, dt, sim_id):
        raise NotImplementedError
