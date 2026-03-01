import yaml
from core.mqtt_client import MQTTClient
from managers.mongo_manager import MongoManager

# Load YAML config
with open("config.yaml") as f:
    config = yaml.safe_load(f)

mqtt_config = config.get("mqtt", {})
mongo_config = config.get("mongo", {})

manager = MongoManager(
    uri=mongo_config.get("uri", "mongodb://localhost:27017"),
    db=mongo_config.get("db", "game"),
)

# Start MQTT client
mqtt = MQTTClient(
    broker=mqtt_config.get("broker", "broker.hivemq.com"),
    port=mqtt_config.get("port", 1883),
    topic=mqtt_config.get("topic", "pisid_mazemov_25"),
    manager=manager,
)

mqtt.start()
