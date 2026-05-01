import sys
import os
import threading

# Add root to path so we can import common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.config_loader import load_config
from common.mongo_connection import get_mongo_db
from common.mysql_connection import MySQLManager

from change_stream import MongoChangeStreamDispatcher

# Import All Workers
from workers.movement import MovementWorker
from workers.temperature import TemperatureWorker
from workers.sound import SoundWorker
from workers.room import RoomWorker
from workers.retry import RetryWorker
from workers.ack import AckWorker

def main():
    print("=== STARTING OUTBOUND SERVICE (Sync MongoDB -> MySQL + ACKs) ===")
    config = load_config()
    
    mqtt_config = config.get("mqtt", {})
    mongo_config = config.get("mongo", {})
    mysql_config = config.get("mysql", {})
    consulting_config = mysql_config.get("consulting", {})

    # 1. Database Connections
    db = get_mongo_db(
        uri=mongo_config.get("uri", "mongodb://localhost:27017"),
        db_name=mongo_config.get("db", "game")
    )

    mysql_manager = MySQLManager(
        host=consulting_config.get("host", "localhost"),
        port=consulting_config.get("port", 3306),
        user=consulting_config.get("user", "aluno"),
        password=consulting_config.get("password", "aluno"),
        database=consulting_config.get("db", "mazerun")
    )
    mysql_manager.connect()

    # 2. MQTT Client (Publisher wrapper)
    import paho.mqtt.client as mqtt_paho
    class MQTTWrapper:
        def __init__(self, broker, port):
            self.client = mqtt_paho.Client(mqtt_paho.CallbackAPIVersion.VERSION1)
            self.client.connect(broker, port, 60)
            threading.Thread(target=self.client.loop_forever, daemon=True).start()

    mqtt_publisher = MQTTWrapper(mqtt_config.get("broker"), mqtt_config.get("port"))

    # 3. Change Stream Dispatcher
    dispatcher = MongoChangeStreamDispatcher(
        mongo_uri=mongo_config.get("uri", "mongodb://localhost:27017"),
        db_name=mongo_config.get("db", "game")
    )

    # 4. Initialize and Start All Workers
    all_workers = [
        # Data processing workers (react to queues)
        MovementWorker(dispatcher.queues["moves"], db, mqtt_publisher, mysql_manager),
        TemperatureWorker(dispatcher.queues["temperature"], db, mqtt_publisher),
        SoundWorker(dispatcher.queues["sound"], db, mqtt_publisher),
        RoomWorker(dispatcher.queues["rooms"], db, mqtt_publisher),
        
        # Maintenance worker (periodic check)
        RetryWorker(db, timeout_seconds=30),
        
        # Finalization worker (react to MQTT ACKs)
        AckWorker(mqtt_config.get("broker"), mqtt_config.get("port"), db)
    ]

    for w in all_workers:
        w.start()

    # 5. Start listening to change stream (blocks main thread)
    try:
        dispatcher.start_listening()
    except KeyboardInterrupt:
        print("Outbound Service stopping...")
        mysql_manager.close()

if __name__ == "__main__":
    main()
