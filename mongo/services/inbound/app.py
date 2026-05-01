import sys
import os

# Add root to path so we can import common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.config_loader import load_config
from common.mongo_connection import get_mongo_db
from processor import InboundProcessor
from mqtt_client import InboundMQTTClient

def main():
    print("=== STARTING INBOUND SERVICE (MQTT -> MongoDB) ===")
    config = load_config()
    
    mqtt_config = config.get("mqtt", {})
    mongo_config = config.get("mongo", {})

    db = get_mongo_db(
        uri=mongo_config.get("uri", "mongodb://localhost:27017"),
        db_name=mongo_config.get("db", "game")
    )

    processor = InboundProcessor(db)
    
    # Filter topics: only those that provide data
    all_topics = mqtt_config.get("topics", [])
    data_topics = [t for t in all_topics if any(p in t for p in ["mazemov", "mazetemp", "mazesound", "mazeact"])]

    mqtt = InboundMQTTClient(
        broker=mqtt_config.get("broker"),
        port=mqtt_config.get("port"),
        topics=data_topics,
        processor=processor
    )

    try:
        mqtt.start()
    except KeyboardInterrupt:
        print("Inbound Service stopping...")

if __name__ == "__main__":
    main()
