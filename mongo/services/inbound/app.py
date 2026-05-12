import sys
import os

# Add root to path so we can import common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.config_loader import load_config
from common.mongo_connection import get_mongo_db
from services.inbound.processor import InboundProcessor
from services.inbound.mqtt_client import InboundMQTTClient

def main():
    print("=== STARTING INBOUND SERVICE (MQTT -> MongoDB) ===")
    config = load_config()
    
    mqtt_config = config.get("mqtt", {})
    mongo_config = config.get("mongo", {})

    # Prefer MONGO_URI from environment (for Docker), fallback to config
    mongo_uri = os.environ.get("MONGO_URI") or mongo_config.get("uri", "mongodb://localhost:27017")

    db = get_mongo_db(
        uri=mongo_uri,
        db_name=mongo_config.get("db", "game")
    )

    processor = InboundProcessor(db)
    
    # Filter topics: only those that provide data + the handshake topic
    all_topics = mqtt_config.get("topics", [])
    data_topics = [t for t in all_topics if any(p in t for p in ["mazemov", "mazetemp", "mazesound", "mazeact"])]
    # Add the trigger topic explicitly so MongoDB can receive the handshake
    if "game/start" not in data_topics:
        data_topics.append("game/start")

    mqtt = InboundMQTTClient(
        broker=mqtt_config.get("broker"),
        port=mqtt_config.get("port"),
        topics=data_topics,
        processor=processor
    )
    
    # Inject the MQTT client as the publisher for ACKs
    processor.mqtt_publisher = mqtt.client

    try:
        mqtt.start()
    except KeyboardInterrupt:
        print("Inbound Service stopping...")

if __name__ == "__main__":
    main()
