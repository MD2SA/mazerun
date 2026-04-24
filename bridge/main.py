import yaml
import threading

from core.mqtt_client import MQTTClient
from managers.mongo_manager import MongoManager
from managers.mysql_manager import MySQLManager
from managers.mongo_change_streams import MongoChangeStreamDispatcher

from handlers.movement_handler import MovementWorker
from handlers.temperature_handler import TemperatureWorker
from handlers.sound_handler import SoundWorker
from handlers.room_handler import RoomWorker

# Load YAML config
with open("config.yaml") as f:
    config = yaml.safe_load(f)

mqtt_config = config.get("mqtt", {})
mongo_config = config.get("mongo", {})
mysql_config = config.get("mysql", {})

mongo_manager = MongoManager(
    uri=mongo_config.get("uri", "mongodb://localhost:27017"),
    db_name=mongo_config.get("db", "game"),
)

mysql_config = config.get("mysql", {})
consulting_config = mysql_config.get("consulting", {})
saving_config = mysql_config.get("saving", {})

mysql_manager = MySQLManager(
    host=consulting_config.get("host", "localhost"),
    port=consulting_config.get("port", 3306),
    user=consulting_config.get("user", "aluno"),
    password=consulting_config.get("password", "aluno"),
    database=consulting_config.get("db", "mazerun")
)

# Connect to MySQL
mysql_manager.connect()

# Start MQTT client
mqtt = MQTTClient(
    broker=mqtt_config.get("broker"),
    port=mqtt_config.get("port"),
    topics=mqtt_config.get("topics"),
    manager=mongo_manager,
)

# Dispatch Change Streamer
dispatcher = MongoChangeStreamDispatcher(
    mongo_uri=mongo_config.get("uri", "mongodb://localhost:27017"),
    db_name=mongo_config.get("db", "game")
)

# Start 4 Independent Thread Workers
movement_worker = MovementWorker(dispatcher.queues["moves"], dispatcher.db, mqtt, mysql_manager)
temperature_worker = TemperatureWorker(dispatcher.queues["temperature"], dispatcher.db, mqtt)
sound_worker = SoundWorker(dispatcher.queues["sound"], dispatcher.db, mqtt)
room_worker = RoomWorker(dispatcher.queues["rooms"], dispatcher.db, mqtt)

movement_worker.start()
temperature_worker.start()
sound_worker.start()
room_worker.start()

# Start MQTT Client in a daemon thread so it doesn't block
threading.Thread(target=mqtt.start, daemon=True).start()

# Start listening to change stream (blocks main thread)
try:
    dispatcher.start_listening()
except KeyboardInterrupt:
    print("Shutting down gracefully...")
    mysql_manager.close()
