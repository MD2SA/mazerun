import sys
import json
import time
import paho.mqtt.client as mqtt
from common.config_loader import load_config
from common.mysql_connection import MySQLConnection

def main():
    if len(sys.argv) < 2:
        print("Usage: python handshake.py <player_id>")
        sys.exit(1)

    try:
        player_id = int(sys.argv[1])
    except ValueError:
        print("Error: player_id must be an integer")
        sys.exit(1)

    config = load_config()
    mysql_config = config.get("mysql", {}).get("saving", {})
    mqtt_config = config.get("mqtt", {})

    # 1. Create simulation in MySQL
    print(f"[Handshake] Connecting to MySQL...")
    db = MySQLConnection(mysql_config)
    if not db.connect():
        print("Error: Could not connect to MySQL")
        sys.exit(1)

    try:
        cursor = db.db.cursor()
        # Using Stored Procedure to create simulation (4 arguments: requester_email, description, team_id, player_id)
        team_id = config.get("team_id", 25)
        cursor.callproc("sp_create_game", ("admin@mazerun.io", "Handshake Session", team_id, player_id))
        
        # Get the result from the SELECT inside the SP
        for result in cursor.stored_results():
            row = result.fetchone()
            if row:
                sim_id = row[0]
        
        db.db.commit()
        cursor.close()
        print(f"[Handshake] ✔ Created Simulation ID: {sim_id} for Player: {player_id}")
    except Exception as e:
        print(f"Error creating simulation: {e}")
        sys.exit(1)
    finally:
        db.close()

    # 2. Notify MongoDB and wait for ACK via MQTT
    ack_received = False
    
    def on_message(client, userdata, msg):
        nonlocal ack_received
        try:
            payload = json.loads(msg.payload.decode())
            # Verify if this ACK matches our simulation
            if payload.get("simulation_id") == sim_id:
                ack_received = True
        except:
            pass

    team_id = config.get("team_id", 25)
    topic_start = f"pisid/{team_id}/game/start"
    topic_ack = f"pisid/{team_id}/game/start/ack"
    print(f"[Handshake] Using isolation topics: START={topic_start}, ACK={topic_ack}")

    print(f"[Handshake] Connecting to MQTT broker {mqtt_config.get('broker')}...")
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(mqtt_config.get("broker"), mqtt_config.get("port"))
    client.subscribe(topic_ack)
    client.loop_start()

    # Wait for ACK with timeout and retries
    timeout = 20
    start_time = time.time()
    last_publish_time = 0
    publish_interval = 3  # Retry publish every 3 seconds

    print(f"[Handshake] Waiting for MongoDB ACK (timeout: {timeout}s)...")

    while not ack_received and (time.time() - start_time) < timeout:
        current_time = time.time()
        if (current_time - last_publish_time) > publish_interval:
            print(f"[Handshake] Publishing start message to {topic_start}...")
            client.publish(topic_start, json.dumps({
                "player_id": player_id,
                "simulation_id": sim_id
            }), qos=1)
            last_publish_time = current_time

        time.sleep(0.5)

    client.loop_stop()
    client.disconnect()

    if ack_received:
        print("[Handshake] ✔ SUCCESS: MongoDB acknowledged the session.")
        # Exit with success so the caller script knows it can proceed
        sys.exit(0)
    else:
        print("[Handshake] ✘ ERROR: Timeout waiting for MongoDB ACK.")
        sys.exit(1)

if __name__ == "__main__":
    main()
