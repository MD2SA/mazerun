import sys
import os

# Add root to path so we can import common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.config_loader import load_config
from common.mongo_connection import get_mongo_db
from common.simulation_config import SimulationConfigRepository
from services.inbound.processor import InboundProcessor
from services.inbound.mqtt_client import InboundMQTTClient

def main():
    print("=== STARTING INBOUND SERVICE (MQTT -> MongoDB) ===")
    config = load_config()
    
    mqtt_config = config.get("mqtt", {})
    mongo_config = config.get("mongo", {})
    mysql_config = config.get("mysql", {}).get("consulting", {})

    # Prefer MONGO_URI from environment (for Docker), fallback to config
    mongo_uri = os.environ.get("MONGO_URI") or mongo_config.get("uri", "mongodb://localhost:27017")

    db = get_mongo_db(
        uri=mongo_uri,
        db_name=mongo_config.get("db", "game")
    )

    team_id = config.get("team_id", 25)
    simulation_configs = SimulationConfigRepository(db, mysql_config)
    processor = InboundProcessor(db, team_id=team_id, simulation_configs=simulation_configs)
    
    # Filter topics: only those that provide raw sensor data
    # We avoid "processed/" topics to prevent loops
    all_topics = mqtt_config.get("topics", [])
    data_topics = []
    for t in all_topics:
        # Must contain sensor keyword and NOT contain "processed" or "persistence"
        is_sensor = any(p in t for p in ["mazemov", "mazetemp", "mazesound", "mazeact"])
        is_internal = any(p in t for p in ["processed", "persistence", "game/start/ack"])
        
        if is_sensor and not is_internal:
            data_topics.append(t)

    # We use a team-specific topic to avoid collisions on public brokers
    team_id = config.get("team_id", 25)
    topic_start = f"pisid/{team_id}/game/start"
    topic_finished = f"pisid/{team_id}/simulation/finished"
    print(f"[Inbound] Configuring for Team {team_id}. Handshake Topic: {topic_start}")
    
    if topic_start not in data_topics:
        data_topics.append(topic_start)
    if topic_finished not in data_topics:
        data_topics.append(topic_finished)

    print(f"[Inbound] Subscribing to topics: {data_topics}")

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
